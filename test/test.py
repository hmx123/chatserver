import hashlib

pwd = '123456'
newpwd = hashlib.sha1(pwd.encode("utf-8")).hexdigest()
print newpwd