import aiohttp
import asyncio
import json
import uuid
from mutagen.wave import WAVE
from time import sleep

endpoint = "https://api.assemblyai.com/v2"

async def auth(api:str ) -> dict:
    ''' '''
    headers = {'authorization': api}
    async with aiohttp.request('GET',  f"{endpoint}/transcript/", headers=headers) as response:
        assert response.status == 200
        return headers


async def _upload(session, file:str, auth:dict )-> None:
    ''' Uploading a file logic'''
    @aiohttp.streamer
    def file_sender(writer, file_name=None):
          with open(file_name, 'rb') as f:
              chunk = f.read(5242880)
              while chunk:
                  yield from writer.write(chunk)
                  chunk = f.read(5242880)
    # Chunk data, and stream
    async with session.post(f'{endpoint}/upload',
                            data=file_sender(file_name=file), headers= auth) as resp:
           return await resp.json()


async def _submit_upload(session, upload_url:str , auth:dict) -> None:
    json = { "audio_url": f"{upload_url}" }
    headers= auth
    async with session.post(f'{endpoint}/transcript', headers= auth, json=json) as response:
        return await response.json()


async def _get_status(auth:dict, transcript_guid:str ):
    headers = {'authorization': api}
    async with aiohttp.request('GET', f"{endpoint}/transcript/{transcript_guid}") as response:
        assert response.status == 200
        return response

async def _get_transcript(auth:dict, transcript_guid:str ):
    async with aiohttp.request('GET', f"{endpoint}/transcript/{transcript_guid}", headers=auth) as response:
        # assert response.status == 200
        return await response.json()
        

async def transcript_print(audio_file, api):
    audio = WAVE(audio_file)
    audio_length = int(audio.info.length)

    async with aiohttp.ClientSession() as session:
        upload_link = await _upload(session, audio_file, {'authorization': api})
        submit = await _submit_upload(session, upload_link['upload_url'], {'authorization': api})
        #print(submit)
        transcript = await _get_transcript({'authorization': api}, submit['id'])
        while transcript:
            if transcript['status'] =='processing' or transcript['status'] =='queued' :
                sleep(audio_length)
                transcript = await _get_transcript({'authorization': api}, submit['id'])
            else:
                break
        print(f'Audio file: {audio_file}')
        collected_text = [(x['text']) for x in transcript['words']]
        
        listToStr = ' '.join(map(str, collected_text))
        print(listToStr)


'''
import requests
endpoint = "https://api.assemblyai.com/v2/transcript/YOUR-TRANSCRIPT-ID-HERE"
headers = {
    "authorization": "YOUR-API-TOKEN",
}
response = requests.get(endpoint, headers=headers)
print(response.json())
'''

'''
endpoint = "https://api.assemblyai.com/v2/transcript"
json = { "audio_url": "https://bit.ly/3yxKEIY" }
headers = {
    "authorization": "YOUR-API-TOKEN",
    "content-type": "application/json"
}
response = requests.post(endpoint, json=json, headers=headers)
print(response.json())

'''

