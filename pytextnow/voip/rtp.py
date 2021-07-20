import argparse
import asyncio
import logging
import os
import random

from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import BYE, TcpSocketSignaling
from aiortc.sdp import candidate_from_sdp

class RTP:
	async def start(self, sdpdata, answer):
		pc = RTCPeerConnection()
#		pc.addTransceiver("audio", direction="sendrecv")


		player = MediaPlayer("audio.wav")

#		recorder = MediaBlackhole()
		recorder = MediaRecorder("record.wav")

		@pc.on("track")
		def on_track(track):
			print("Track %s received" % track.kind)
			recorder.addTrack(track)

		sdpdata += "a=sendrecv\r\n"

		await pc.setRemoteDescription(RTCSessionDescription(type="offer", sdp=sdpdata))
		await recorder.start()
		pc.addTrack(player.audio)

		await pc.setLocalDescription(await pc.createAnswer())
		await answer(bytes(pc.localDescription.sdp, "UTF-8"))

		for i in sdpdata.split("\r\n"):
			if i.startswith("a=candidate"):
				candidate = candidate_from_sdp(i[2:])
				candidate.sdpMid = "audio"
				await pc.addIceCandidate(candidate)

		player._start(player.audio)
