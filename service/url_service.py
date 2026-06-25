from repository.url_repo import UrlRepo

class UrlService:
    def __init__(self):
        self._urlrepo=UrlRepo()
        self.BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def get_short_url(self,org_url:str):
        url_id=self._urlrepo.add_url(url=org_url)
        short_code=self.encode_id(url_id)
        return {"short_url": f"http://localhost:8000/{short_code}"}


    def encode_id(self,id:int)->str:
        if id==0:
            return self.BASE62_ALPHABET[0]
        short_code_chars=[]
        while id>0:
            reminder=id%62
            corresponding_char=self.BASE62_ALPHABET[reminder]
            short_code_chars.append(corresponding_char)
            id=id//62
        short_code_chars.reverse()
        return "".join(short_code_chars)
    
    def decode_code(self, code: str) -> int:
        db_id = 0
        for char in code:
            cor_num = self.BASE62_ALPHABET.index(char)            
            db_id = (db_id * 62) + cor_num            
        return db_id
    
    def get_website(self,short_url:str):
        id=self.decode_code(code=short_url)
        org_url=self._urlrepo.fetch_url(id=id)
        return org_url


