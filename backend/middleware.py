"""Bound request bytes before multipart/JSON parsing, including chunked bodies."""
from starlette.responses import JSONResponse

class RequestSizeLimit:
    def __init__(self,app,max_bytes=6*1024*1024):self.app,self.max_bytes=app,max_bytes
    async def __call__(self,scope,receive,send):
        if scope['type']!='http' or scope['method'] not in ('POST','PUT','PATCH'):
            return await self.app(scope,receive,send)
        chunks=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            body=message.get('body',b'');size+=len(body)
            if size>self.max_bytes:
                response=JSONResponse(status_code=413,content={'success':False,'message':'Request too large','data':None,'errors':['Maximum request: 6 MB']})
                return await response(scope,receive,send)
            chunks.append(body)
            if not message.get('more_body',False):break
        delivered=False
        async def limited_receive():
            nonlocal delivered
            if not delivered:
                delivered=True
                return {'type':'http.request','body':b''.join(chunks),'more_body':False}
            return await receive()
        await self.app(scope,limited_receive,send)
