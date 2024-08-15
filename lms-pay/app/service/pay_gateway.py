import asyncio


class PaymentGateway:
    def __init__(self):
        pass

    async def process_payment(self, *, transaction):
        asyncio.sleep(5)
        if transaction["payment_method"] == "credit_card":
            return await self.process_credit_card(transaction)
        else:
            return await self.process_gateway(transaction)
    
    async def process_credit_card(self, transaction):
        await asyncio.sleep(5)
        if transaction["payment_info"]["card_number"] == "4111111111111111":
            return {"status": False, "message": "Card declined"}
        elif transaction["amount"] > 1000:
            return {"status": False, "message": "Amount exceeds limit"}
        
        return {"status": True, "message": "Payment processed"}
    
    async def process_gateway(self, transaction):
        await asyncio.sleep(5)
        return {"redirect_url": "https://gateway.com/redirect", "token": "4811f1b1-1b1b-1b1b-1b1b"}

    
paymentGateway = PaymentGateway()
        

        
        