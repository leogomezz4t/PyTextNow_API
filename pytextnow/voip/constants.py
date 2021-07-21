from hashlib import md5

class Constants:
	def force_bytes(self, value):
		try:
			if type(value) == int:
				value = str(value)
			if type(value) == str:
				value = value.encode("UTF-8")
			if type(value) != bytes:
				value = bytes(value) # Last resort
		finally:
			return value

	sequence = 1
	def generate_packet(self, type, cid=None, seq=None, args=None):
		if seq == None:
			seq = self.sequence
			self.sequence += 1
		seq = self.force_bytes(seq)

		type = self.force_bytes(type)
		if args:
			args = [self.force_bytes(i) for i in args]

		type = type.lower()
		packet = None

		if type == b"register":
			packet = self.RegisterPacket
			if args and args[0]:
				packet = packet.replace(b"{{.authorization}}", self.generate_auth(args[0]))
			else:
				packet = packet.replace(b"\r\n{{.authorization}}", b"")
		elif type == b"trying":
			packet = self.Trying
			packet = packet.replace(b"{{.rec-route_via}}", args[0])
			packet = packet.replace(b"{{.from}}", args[1])
			packet = packet.replace(b"{{.from_addr}}", args[2])
			packet = packet.replace(b"{{.from_tag}}", args[3])
		elif type == b"keepalive":
			packet = self.KeepAlive
			packet = packet.replace(b"{{.from_tag}}", args[0])
		elif type == b"accept":
			packet = self.AcceptCall
			packet = packet.replace(b"{{.rec-route_via}}", args[0])
			packet = packet.replace(b"{{.len}}", str(len(args[1])).encode("UTF-8"))

		if packet:
			packet = packet.replace(b"{{.seq}}", seq)
			if cid:
				packet = packet.replace(b"{{.cid}}", self.force_bytes(cid))
			packet = packet.replace(b"\n", b"\r\n")
			packet = packet.replace(b"\t", b"")
			return packet
		else:
			raise ValueError("Unknown packet type: '%s'" % type.decode("UTF-8"))

	def generate_auth(self, nonce):
		username = self.username.decode('utf-8')
		password = self.password.decode('utf-8')
		method = 'REGISTER'
		realm = 'prod.tncp.textnow.com'
		uri = 'sip:'+realm
		if type(nonce) == bytes:
			nonce = nonce.decode('utf-8')

		# HTTP Digest algorithim
		str1 = md5("{}:{}:{}".format(username,realm,password).encode('utf-8')).hexdigest()
		str2 = md5("{}:{}".format(method,uri).encode('utf-8')).hexdigest()
		str3 = md5("{}:{}:{}".format(str1,nonce,str2).encode('utf-8')).hexdigest()

		# Encode values to b'' instead of '' so that the substitution works
		print(realm, nonce, uri, str3)
		realm = self.force_bytes(realm)
		nonce = self.force_bytes(nonce)
		uri = self.force_bytes(uri)
		response = self.force_bytes(str3)
		print(realm, nonce, uri, response)

		return b'Authorization: Digest username="%s", realm="%s", nonce="%s", uri="%s", response="%s", algorithm=MD5' % (self.force_bytes(username), realm, nonce, uri, response)

	def __init__(self, sip_info=None):
		sip_info = sip_info["tncp"]["credentials"]
		self.username = sip_info["username"]
		self.password = sip_info["password"]
		self.number = self.username.split("_")[0]

		self.username = self.force_bytes(self.username)
		self.password = self.force_bytes(self.password)
		self.number = self.force_bytes(self.number)

		# Hardcoded values below (TODO: find better way to do this)
		self.RegisterPacket = b"""REGISTER sip:prod.tncp.textnow.com SIP/2.0
		Via: SIP/2.0/WSS q72jr0k8gorn.invalid;branch=z9hG4bK428540716
		Max-Forwards: 70
		To: <sip:"""+self.username+b"""@prod.tncp.textnow.com>
		From: <sip:"""+self.username+b"""@prod.tncp.textnow.com>
		Call-ID: 69e069a5-5d2e-4514-9c40-2fbad9e3b8ee
		CSeq: {{.seq}} REGISTER
		Contact: <sip:20n17932@q72jr0k8gorn.invalid;transport=ws>;reg-id=1;+sip.instance="<urn:uuid:86753098-6753-0986-7590-986753098675>";expires=15
		{{.authorization}}
		Expires: 30
		Allow: INVITE,ACK,CANCEL,BYE,UPDATE,MESSAGE,OPTIONS,REFER,INFO
		Supported: path, gruu, outbound
		User-Agent: TextNow CAPI/21.24.0 Android/21.24.1.1
		Content-Length: 0\n\n"""

		self.KeepAlive = b"""OPTIONS sip:b"""+self.username+b"""@prod.tncp.textnow.com SIP/2.0
		Via: SIP/2.0/WSS 4mojsn30fe15.invalid;branch=z9hG4bK889487
		Max-Forwards: 70
		To: <sip:"""+self.username+b"""@prod.tncp.textnow.com>
		From: <sip:"""+self.username+b"""@prod.tncp.textnow.com>;tag={{.from_tag}}
		Call-ID: {{.cid}}
		CSeq: {{.seq}} OPTIONS
		Supported: outbound
		User-Agent: TextNow CAPI/21.24.0 Android/21.24.1.1
		Content-Length: 0\n\n"""

		self.Trying = b"""SIP/2.0 100 Trying
		{{.rec-route_via}}
		To: <sip:"""+self.number+b"""@prod.tncp.textnow.com>
		From: "{{.from}}"<sip:{{.from}}@{{.from_addr}}>;tag={{.from_tag}}
		Call-ID: {{.cid}}
		CSeq: {{.seq}}
		Supported: gruu, outbound
		User-Agent: SIP.js/0.11.6
		Content-Length: 0\n\n"""

		self.AcceptCall = b"""SIP/2.0 200 OK
		{{.rec-route_via}}
		To: <sip:b"""+self.username+b"""@prod.tncp.textnow.com>;tag={{.to_tag}}
		From: <sip:b"""+self.username+b"""@prod.tncp.textnow.com>;tag={{.from_tag}}
		Call-ID: {{.cid}}
		CSeq: {{.seq}}
		Server: sip-proxy-ws2.tncp
		Allow: INVITE,ACK,CANCEL,BYE,UPDATE,MESSAGE,OPTIONS,REFER,INFO
		Content-Type: application/sdp
		Content-Length: {{.len}}\n\n"""
