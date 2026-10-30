import sys, ssl, asyncio, edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
voice, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
rate = sys.argv[4] if len(sys.argv) > 4 else "+0%"
asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(out))
