from algopy import ARC4Contract, String
from algopy.arc4 import abimethod, Address
from algopy import ARC4Contract, arc4, UInt64, String, Bytes, itxn, Global, Asset, Txn, gtxn

class Algoxange(ARC4Contract):
    assetid: UInt64
    unitaryprice: UInt64

    @abimethod(allow_actions=["NoOp"], create="require")
    def create_application(self, asset_id: Asset, unitary_price: UInt64) -> None:
        self.assetid = asset_id.id
        self.unitaryprice = unitary_price
    
    @abimethod()
    def update_asset_id(self, asset_id: Asset) -> None:
        assert Txn.sender == Global.creator_address
        self.assetid = asset_id.id
    

    @abimethod()
    def set_price(self, unitary_price: UInt64) -> None:
        assert Txn.sender == Global.creator_address
        self.unitaryprice = unitary_price

    @abimethod()
    def opt_in_to_asset(self, mbrpay: gtxn.PaymentTransaction) -> None:
        assert Txn.sender == Global.creator_address
        assert not Global.current_application_address.is_opted_in(Asset(self.assetid))

        assert mbrpay.receiver == Global.current_application_address

        assert mbrpay.amount == Global.min_balance + Global.asset_opt_in_min_balance

        itxn.AssetTransfer(
            xfer_asset= self.assetid,
            asset_receiver= Global.current_application_address,
            asset_amount= 0,
        ).submit()

    @abimethod()
    def debug_buy_check(self, buyerTxn: gtxn.PaymentTransaction) -> UInt64:
        if buyerTxn.sender != Txn.sender:
            return UInt64(1)
        if buyerTxn.receiver != Global.current_application_address:
            return UInt64(2)
        if buyerTxn.amount != self.unitaryprice:
            return UInt64(3)
        return UInt64(0)  # All good


    @abimethod()
    def buy(self, buyerTxn: gtxn.PaymentTransaction) -> None:

        assert(buyerTxn.sender == Txn.sender )
        assert(buyerTxn.receiver == Global.current_application_address )
        assert(buyerTxn.amount == self.unitaryprice )


        itxn.AssetTransfer(
            xfer_asset=self.assetid,
            asset_receiver=Txn.sender,
            asset_amount=1,
        ).submit()

    @abimethod(allow_actions=["DeleteApplication"])
    def delete_application(self) -> None:

        assert Txn.sender == Global.creator_address


        itxn.AssetTransfer(
            xfer_asset=self.assetid,
            asset_receiver=Global.creator_address,
            asset_amount=0,
            asset_close_to=Global.creator_address,
            fee=1_000,
        ).submit()

        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address,
            fee=1_000,
        ).submit()


