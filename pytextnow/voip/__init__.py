import random, string
def fixpack(packet, from_addr, from_tag):
	packet = packet.decode("UTF-8").split("\r\n")
	pack = []
	for i in packet:
		if i.startswith("o="):
			pack.append(i.replace("0.0.0.0", "127.0.0.1"))
#		elif i.startswith("c=IN IP4"):
#			pack.append("c=IN IP4 67.180.35.237")
		elif i.startswith("m=audio"):
			pack.append(i.replace("UDP/TLS/", "").replace(" 102", " 101"))
		elif i.startswith("a=group:BUNDLE"):
			pass
		elif i.startswith("a=msid:"):
			pass
#		elif i.startswith("a=candidate:") and (not ("67.180.35.237" in i)):
#			pass
		elif i.startswith("a=end-of-candidates"):
			pass
		elif i.startswith("a=rtpmap:102"):
			pass
		else:
			pack.append(i)

#	pack = pack[:-1] # Remove final \r\n

	for i in ["a=rtpmap:101 telephone-event/8000", "a=fmtp:101 0-15"]:
		pack.append(i)

#	pack.append("") # Re-add final \r\n

	packet = "\r\n".join(pack)

#	pack_len = len(packet.split("\r\n\r\n")[1])
#	packet = packet.replace("{{.len}}", str(pack_len))
#	packet = packet.replace("{{.from_addr}}", from_addr)
#	packet = packet.replace("{{.to_tag}}", ''.join(random.choices(string.ascii_letters + string.digits, k=16)))

	return packet.encode("UTF-8")

import asyncio
import websockets
import threading # For temporary keepalive hack
import time
from pytextnow.voip.constants import Constants
from pytextnow.voip import settings
from pytextnow.voip.rtp import RTP

class VOIP:
	def __init__(self, sip_info):
		self.constants = Constants(sip_info)
		asyncio.get_event_loop().run_until_complete(self.main())

	async def main(self):
		uri = "wss://ws.prod.tncp.textnow.com/"
		print("Connecting...")
		async with websockets.connect(uri, ssl=True, subprotocols=["sip"], extensions=[]) as websocket:
			# Try to register without authentication (so we can get the nonce to authenticate)
			print("Attempting to register without authentication...")
			await websocket.send(self.constants.generate_packet("register"))

			# Get nonce and actually authenticate
			while True:
				got = await websocket.recv()
				if got.startswith("SIP/2.0 401 Unauthorized"):
					print("Needs authentication, generate digest...")
					# Request for authentication!
					www_auth = [i for i in got.split("\r\n") if "WWW-Authenticate" in i][0]
					nonce = [i for i in www_auth.split(" ") if "nonce=" in i][0]
					# Split at equals, get second half, then remove first and last chars (quotes)
					nonce = nonce.split("=")[1][1:-1]
					print("Nonce", nonce)
					packet = self.constants.generate_packet("register", args=(nonce,))
					print("Packet", packet)
					await websocket.send(packet)
					print("(Hopefully) Authenticated.")
					break
				elif got.startswith("SIP/2.0 200 OK"):
					print("Already authenticated!")
					break
				else:
					print("Unknown packet:", got)

			def keepalive():
				while True:
					payload = self.constants.generate_packet("KeepAlive", args=(b"hd83nd9nwh",))
					print("[keepalive] Sending keepalive:", payload, "\n[keepalive] End of keepalive.")
					websocket.send(payload)
					time.sleep(15)

#			keepalive_thread = threading.Thread(target=keepalive, daemon=True)
#			keepalive_thread.start()

			print("Waiting for incoming call.")
			while True:
				got = await websocket.recv()
				if got.startswith("INVITE"):
					print("Received invitation to call!")
					# got[0] = Headers, got[1] = Body
					# Each element of `got` is split at CRLF
					got = [i.split("\r\n") for i in got.split("\r\n\r\n")]
					caller = [i for i in got[0] if i.startswith("f:")][0]
					caller = caller.split("\"")[1]
					if caller in settings.ACCEPTED_NUMBERS:
						conn = [i for i in got[1] if i.startswith("a=candidate")][0]
						addr, port = conn.split(" ")[4:6]
						print("Invited to connect to:", addr, ":", port)

						record_route_via = []
						seq = None
						cid = None
						from_addr = None
						from_tag = None
						for i in got[0]:
							j=bytes(":".join(i.split(":")[1:]), "UTF-8")
							if i.startswith("CSeq:"):
								seq = j
							elif i.startswith("i:"):
								cid = j
							elif i.startswith("v:"):
								from_addr = [z for z in i.split(";") if z.startswith("received=")][0]
								from_addr = from_addr.split("=")[1]
								from_addr = bytes(from_addr, "UTF-8")

								record_route_via.append(bytes("Via:"+i[2:], "UTF-8"))
							elif i.startswith("f:") or i.startswith("From:"):
								from_tag = bytes(i.split(";tag=")[-1], "UTF-8")

							for k in ["Via:", "Record-Route"]:
								if i.startswith(k):
									record_route_via.append(bytes(i, "UTF-8"))


						print("Sending 100 Trying...")
						record_route_via = b"\r\n".join(record_route_via)
						trying = self.constants.generate_packet("Trying", cid=cid, seq=seq, args=(record_route_via, caller, from_addr, from_tag))
						await websocket.send(trying)
						print("Sent 100 Trying.")

						async def answer(message):
							message = fixpack(message, from_addr.decode("UTF-8"), from_tag.decode("UTF-8"))
							packet = self.constants.generate_packet("Accept", cid=cid, seq=seq, args=(record_route_via, message))
							print("Accepting with: ", packet)
							await websocket.send(packet)

						print("Doing the thing!")
						sdp = "\r\n".join(got[1])
						rtp = RTP()
						await rtp.start(sdp, answer)
						print("Done the thing!")

#						print("Sent accept")
#						while True:
#							try:
#								print(">", await websocket.recv())
#							except:
#								pass
					else:
						print("TODO: Reject call")
				elif got.startswith("SIP/2.0 200 OK"):
					print("Got a 200 OK")
				elif got.startswith("ACK"):
					print("Got an ACK")
				else:
					print("Unknown packet:", got)
