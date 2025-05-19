import asyncio

import json

import os

import logging

from telethon import TelegramClient

from telethon .tl. functions . channels import GetParticipantsRequest

from telethon .tl. types import ChannelParticipantsSearch ,

ChannelParticipantsAdmins

import time

# Setup logging

logging . basicConfig ( filename =’error .log ’, level = logging .ERROR ,

format =’%( asctime )s - %( levelname )s - %( message )s’

)

CONFIG_FILE = ’config . json ’

def load_config () :

""" Load configuration from config . json if it exists ."""

if os. path . exists ( CONFIG_FILE ):

with open ( CONFIG_FILE , ’r’) as f:

return json . load (f)

return {}

def save_config ( api_id , api_hash , phone_number ):

""" Save configuration to config . json ."""

config = {’api_id ’: api_id , ’api_hash ’: api_hash , ’ phone_number ’:

phone_number }

with open ( CONFIG_FILE , ’w’) as f:

json . dump (config , f, indent =4)

def get_config () :

""" Get API credentials and phone number from user or config file .

"""

config = load_config ()

if config :



print (" Loaded saved configuration .")



return config [’api_id ’] , config [’api_hash ’] , config [’

phone_number ’]

api_id = input (" Enter your API ID: ")

api_hash = input (" Enter your API Hash : ")

phone_number = input (" Enter your phone number (e.g. , +1234567890) :

")

save_choice = input (" Save configuration for future use ? (yes /no):

"). lower ()

if save_choice == ’yes ’:

save_config (api_id , api_hash , phone_number )

return api_id , api_hash , phone_number

async def get_groups ( client ):

""" Fetch all groups the user is part of."""

groups = []

async for dialog in client . iter_dialogs () :

if dialog . is_group or dialog . is_channel :

groups . append ( dialog )

return groups

async def get_admins_and_owner (client , group ) :

""" Fetch all admins and the owner of the group ."""

admin_ids = set ()

# Get admins

async for participant in client . iter_participants (group , filter =

ChannelParticipantsAdmins ):

admin_ids .add ( participant . user_id )

# Get group creator ( owner )

participants = await client ( GetParticipantsRequest (

group , ChannelParticipantsSearch (’’) , 0 , 1 , hash =0

))

for participant in participants . participants :

if hasattr ( participant , ’creator ’) and participant . creator :

admin_ids .add ( participant . user_id )

return admin_ids

async def remove_members (client , group ):

""" Remove all members from the specified group except admins and

owner ."""

offset = 0

limit = 100

total_removed = 0

total_members = 0

# Get admin and owner IDs



protected_ids = await get_admins_and_owner (client , group )



# Get total member count

participants = await client ( GetParticipantsRequest (

group , ChannelParticipantsSearch (’’) , 0 , 1 , hash =0

))

total_members = participants . count

print (f" Total members to process : { total_members }")

while True :

participants = await client ( GetParticipantsRequest (

group , ChannelParticipantsSearch (’’) , offset , limit , hash

=0

) )

if not participants . users :

break

for user in participants . users :

if user .id not in protected_ids : # Skip admins and owner

try :

await client . kick_participant (group , user )

total_removed += 1

print (f" Removed { user . first_name or ’Unknown ’} (ID

: { user .id }) "

f"[{ total_removed }/{ total_members }]")

time . sleep (1) # Avoid rate limits

except Exception as e:

logging . error (f" Failed to remove { user . first_name

or ’Unknown ’} (ID: { user .id }): {e}")

print (f" Failed to remove { user . first_name or ’

Unknown ’}: Check error .log ")

# Check for pause or cancel

if total_removed % 10 == 0:

action = input (" Pause (p), Cancel (c), or Continue

( enter ): ") . lower ()

if action == ’p’:

input (" Paused . Press Enter to resume ... ")

elif action == ’c’:

print (" Operation cancelled .")

return total_removed

offset += len ( participants . users )

return total_removed

async def main () :

# Get configuration

api_id , api_hash , phone_number = get_config ()

# Initialize client



client = TelegramClient (’ session_name ’, api_id , api_hash )



await client . start ( phone = phone_number )

print (" Logged in successfully !")

while True :

print ("\n=== Telegram Group Cleaner === ")

print ("1. List Groups ")

print ("2. Clean Group ")

print ("3. Exit ")

choice = input (" Enter option (1 -3): ")

if choice == ’1’:

groups = await get_groups ( client )

print ("\ nYour groups :")

for i, group in enumerate (groups , 1) :

print (f"{i}. { group . title } (ID: { group .id })")

elif choice == ’2’:

groups = await get_groups ( client )

print ("\ nYour groups :")

for i, group in enumerate (groups , 1) :

print (f"{i}. { group . title } (ID: { group .id })")

try :

group_choice = int ( input ("\ nEnter the number of the

group to clean : ")) - 1

if 0 <= group_choice < len ( groups ) :

selected_group = groups [ group_choice ]

print (f" Selected group : { selected_group . title }")

confirm = input (f"Are you sure you want to remove

ALL members ( except admins and owner ) from {

selected_group . title }? (yes /no): ") . lower ()

if confirm == ’yes ’:

removed = await remove_members (client ,

selected_group )

print (f" Finished cleaning { selected_group .

title }. Removed { removed } members .")

else :

print (" Operation cancelled .")

else :

print (" Invalid group number .")

except ValueError :

print (" Please enter a valid number .")

elif choice == ’3’:

print (" Exiting ... ")

break

else :

print (" Invalid option . Please try again .")



await client . disconnect ()



if __name__ == ’__main__ ’:

asyncio .run ( main () )

  
