---
title: A Simpler Way to Build DVMs
date: 2025-08-01
summary: DVMs let you offer APIs without domains or SEO hassles. This practical guide cuts through the complexity with a streamlined approach: just 3 event kinds, simple request/response patterns, and complete code examples to get you running in minutes.
slug: a-simpler-way-to-build-dvms
tags: nostr, data vending machine, api, ecash, lightning, nostr wallet connect
headerImage: assets/writing/a-simpler-way-to-build-dvms-header.webp
nostrEvent: 23f410ed988899f3c5cef79f099f15f676cb15122c66c197c90e66f9f6196044
nostrDtag: 1754018912170
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
Want to offer an API without dealing with domains or SEO? `Data Vending Machine (DVM)` is a fun name for what is essentially an API over Nostr. It's incredible because anyone in the world can offer a (free or paid) computational service without having to register a domain name, and without having to do SEO optimization begging for search engines to list them; instead they simply post an announcement to Nostr relays and get listed in online DVM marketplaces.

Do you want to offer such a service? This is how I would build a DVM today. If you want to know more about how myself and others arrived at these recommendations, check out my other articles!

### What you need to have before building your DVM

1. A computational service that you want to offer
2. Preferred list of relays (this should be relays where your users are and that are DVM friendly, such as supporting higher rate limits)

### Steps to build your DVM

1. Generate the Nostr keypair (npub/nsec) for your DVM. Every DVM needs it's own keypair.
2. Write the documentation for how people will use your computational service. Specify inputs, outputs, and error messages.
3. Host the documentation somewhere (you could broadcast it as a wiki event kind 30818 or at a URL).
4. Create the kind 11999 announcement for your DVM for people to use it. It should reference the documentation, along with other data (see example below). Sign the announcement with your DVM nsec and broadcast it to your relays.
5. Integrate common Nostr library functions with your computational service, so it can receive job requests and return responses back to users. 
6. Run your DVM!

**Note on Encryption:** This guide focuses on the core DVM pattern without encryption. An encrypted version using NIP-17/NIP-59 patterns is being developed and will be covered in a follow-up guide. The fundamentals you learn here will directly apply to the encrypted version.

We'll now walk through each step and give as much context as possible. If you give this to your LLM, it should be able to vibe code this for you. Also, at the end we link to a Github repository with full working examples.

## Step 1 of 6: Generate a Nostr Keypair for your DVM

There are many libraries and tools to do this, such as rust-nostr (with bindings for Python, C#, Kotlin, Swift, JavaScript), nak the command line swiss army nostr tool, and ndk (javascript).

### Option A: rust-nostr python bindings

	pip install nostr-sdk
	
After installing, run like:

```python
from nostr_sdk import Keys, SecretKey, PublicKey
	
# Method 1: Generate completely new random keys
keys = Keys.generate()
secret_key = keys.secret_key()
public_key = keys.public_key()
	
# Display keys in different formats
print("=== New Generated Keys ===")
print(f"Secret Key (nsec): {secret_key.to_bech32()}")
print(f"Public Key (npub): {public_key.to_bech32()}")
print(f"Secret Key (hex):  {secret_key.to_hex()}")
print(f"Public Key (hex):  {public_key.to_hex()}")
```

### Option B: nak Command Line Tool

nak is a powerful command-line tool for all Nostr operations, including key generation.

```bash
# Install nak (requires Go)
go install github.com/fiatjaf/nak@latest

# Or download binary from releases
# https://github.com/fiatjaf/nak/releases
```

 Basic Key Generation

```bash
# Generate a new private key
nak key generate
```

### Option C: NDK (JavaScript/TypeScript)


NDK is a comprehensive Nostr development kit for JavaScript/TypeScript applications.

### Installation

```bash
npm install @nostr-dev-kit/ndk
# or
yarn add @nostr-dev-kit/ndk
```

Basic Key Generation (Node.js)

```javascript
import NDK, { NDKPrivateKeySigner } from '@nostr-dev-kit/ndk';
import { generateSecretKey, getPublicKey } from 'nostr-tools/pure';
import { nip19 } from 'nostr-tools';

// Method 1: Generate new keys
function generateNewKeys() {
    const secretKey = generateSecretKey();
    const publicKey = getPublicKey(secretKey);
    
    // Convert to bech32 format
    const nsec = nip19.nsecEncode(secretKey);
    const npub = nip19.npubEncode(publicKey);
    
    console.log('=== New Generated Keys ===');
    console.log(`Secret Key (hex):  ${Buffer.from(secretKey).toString('hex')}`);
    console.log(`Secret Key (nsec): ${nsec}`);
    console.log(`Public Key (hex):  ${publicKey}`);
    console.log(`Public Key (npub): ${npub}`);
    
    return { secretKey, publicKey, nsec, npub };
}
```


## Step 2 of 6: Write the documentation

Your documentation should include descriptions and examples of each step of using the DVM. A good example of this is the [Vertex DVM documentation]( https://vertexlab.io/docs/services/).

Make sure you include the following in your docs: 
- input format with examples
- response format with examples
- error responses with examples
- any intermediate responses, such as asking for payment

## Step 3 of 6: Host your documentation online somewhere

If you want to be Nostr only, publish your documentation via a wiki kind event [as described here]( https://habla.news/u/dustind@dtdannen.github.io/1743798227950) and use a `d` tag like 'dvm-documentation'

Otherwise, you can host the documentation at a URL and link that URL in the documentation tag instead.

## Step 4 of 6: Announce your DVM

Create an event like the following and fill it in with your relevant details:

```json
{
  "kind": 11999,
  "pubkey": "<dvm-pubkey-generated-in-step-1>",
  "created_at": 1000000000,
  "tags": [
    ["name", "My Cool DVM"], // Human-readable DVM name
    ["documentation", "30818:<dvm-pubkey-generated-in-step-1>:dvm-documentation"], // or url if hosting the old school way
    ["picture", " https://example.com/dvm.png"], // DVM or Brand Image
    ["website", " https://example.com"], // DVM website if you have one
    ["support_encryption"], // Presence indicates DVM supports encrypted messages
    ["t", "algorithmic-feed"], // self-declared category 
    ["relays", "<your-preferred-relay1>", "<your-preferred-relay2>", "..."] // relays where users can find your DVM
  ]
}
```

**Note:** while the `t` tag is a self-declared category for your DVM, if you want to compete against other existing DVMs, use the same category that they do. If you're the first one to offer a DVM of this type, choose any category you'd like.

## Step 5 of 6: Integrate Nostr Library Functions with Your Computational Service

Building a DVM is simpler than you might think. The old spec (original NIP-90) required that you choose a kind number, but this new approach doesn't require choosing any kind numbers. Here are the kinds you should use:

- **Kind 11999**: DVM announcement
- **Kind 25000**: Both job requests AND responses
- **Kind 11998**: Heartbeat events to show your DVM is online

The beauty of this approach is that responses use the same kind as requests, and all DVMs use the same kind number. You can tell them apart because responses containing a DVM's output will tag the original request event and come from a different pubkey (your DVM's pubkey).

Here are code snippets to do all the major functions of running your DVM. For a full working example, see [this github repo]( https://github.com/dtdannen/new-dvm-examples).

### Setting Up the Foundation

First, let's install the rust-nostr Python bindings. The python bindings for rust-nostr is the nostr-sdk library:

```bash
pip install nostr-sdk
```


### A Base DVM Class for Simpler Code

To make the rest of this guide easier, here is a base class that contains important variables and the client object, which is used by rust-nostr to communicate with relays.

```python
import asyncio
from typing import Dict, List, Optional
from nostr_sdk import (
    Client, Keys, EventBuilder, Filter, Kind, Tag, Timestamp, 
    Event, HandleNotification, RelayMessage, NostrSigner, RelayUrl
)

class BaseDVM:
    """
    Simple DVM implementation using the new streamlined approach
    """
    
    def __init__(self, 
                 keys: Keys, 
                 relay_urls: List[str],
                 dvm_name: str,
                 category: str = "general"):
        self.keys = keys
        self.relay_urls = relay_urls
        self.dvm_name = dvm_name
        self.category = category  # e.g., "translation", "image-generation", etc.
        self.client = None
        
        # Track processed jobs to avoid duplicates
        self.processed_jobs = set()
        
        print(f"Initializing {dvm_name}")
        print(f"Category: {category}")
        print(f"DVM Public Key: {self.keys.public_key().to_bech32()}")
```

Next, let's add the initialization method that connects to relays and starts listening for job requests:

```python
async def initialize(self):
        """Initialize the Nostr client and connect to relays"""
        signer = NostrSigner.keys(self.keys)
        self.client = Client(signer)
        
        # Add relays
        for relay_url in self.relay_urls:
            relay = RelayUrl.parse(relay_url)
            await self.client.add_relay(relay)
            print(f"Added relay: {relay_url}")
        
        # Connect to relays
        await self.client.connect()
        print("Connected to relays")
        
        # Subscribe to job requests
        await self.subscribe_to_job_requests()
```

Here's how to subscribe to job requests from users:

```python
    async def subscribe_to_job_requests(self):
        """Subscribe to DVM job requests - both open and targeted requests"""
        
        # Filter 1: Open requests (category-based) - any DVM can respond
        open_filter = (Filter()
                      .kind(Kind(25000))
                      .hashtag(self.category)
                      .since(Timestamp.now()))
        
        # Filter 2: Targeted requests (p-tag based) - specifically targeting this DVM
        targeted_filter = (Filter()
                          .kind(Kind(25000))
                          .reference(f"p:{self.keys.public_key().to_hex()}")
                          .since(Timestamp.now()))
        
        # Subscribe to both filters
        open_subscription = await self.client.subscribe(open_filter)
        targeted_subscription = await self.client.subscribe(targeted_filter)
        
        print(f"Subscribed to OPEN job requests (category '{self.category}'): {open_subscription}")
        print(f"Subscribed to TARGETED job requests (p-tag): {targeted_subscription}")
```

The subscription logic is straightforward. We listen for job requests in one of two possible ways:

1. Jobs specifically tagged to our DVM's pubkey
2. Jobs that use our category as a hashtag

This gives users multiple ways to find and use your DVM. Feel free to support one or both of these job requests; and make sure to explain your choice(s) in your documentation.

### Processing Job Requests

Now for the core functionality - processing jobs. The key insight is that both requests and responses use kind 25000, but responses always tag the original request event id. 

```python
    def extract_input_from_event(self, event: Event) -> str:
        """Extract input data from job request event"""
        # Look for 'i' tag (input tag per DVM conventions)
        for tag in event.tags():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "i":
                return tag_vec[1]
        
        # Fallback to event content if no 'i' tag
        return event.content()
```

The original DVM spec used `i` tags to specify inputs. Because this is a simple example, we use it because it's convenient, but you don't have to do it this way. However you decide to do it, you must define and explain it via your documentation.

```python   
    def extract_job_params(self, event: Event) -> Dict[str, str]:
        """Extract job parameters from event tags"""
        params = {}
        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 3 and tag_vec[0] == "param":
                param_name = tag_vec[1]
                param_value = tag_vec[2]
                params[param_name] = param_value
        return params
    
    def is_job_request(self, event: Event) -> bool:
        """Check if this event is a job request (not a response)"""
        # If it tags another event, it's probably a response
        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "e":
                return False
        
        # If it has input data, it's likely a request
        return bool(self.extract_input_from_event(event))
    
    def is_targeted_request(self, event: Event) -> bool:
        """Check if this is a targeted request (has p-tag with our pubkey)"""
        our_pubkey_hex = self.keys.public_key().to_hex()
        for tag in event.tags().to_vec():
            tag_vec = tag.as_vec()
            if len(tag_vec) >= 2 and tag_vec[0] == "p" and tag_vec[1] == our_pubkey_hex:
                return True
        return False
```

These helper methods are simply arbitrary examples. You may need different ways to extract the data from job requests, and your documentation should clearly and comprehensively explain how to do so, with examples.

### Implementing Your Computational Service

Here's where you add your actual business logic. This method should be overridden in your specific DVM implementation:

```python
    async def process_job_request(self, event: Event) -> Optional[str]:
		"""Process echo job - just return the input"""
		input_data = self.extract_input_from_event(event)
		if not input_data:
			return None
			
		print(f"Echoing: {input_data}")
		
		# Just echo back the input
		return f"Echo: {input_data}"
```

### Sending Responses

The response mechanism is elegant in its simplicity. We use the same event kind (25000) but tag the original request, this is the snippet on sending the job result:

```python
    async def send_job_result(self, 
                            original_event: Event, 
                            result: str, 
                            success: bool = True) -> Event:
        """Send job result using the same event kind as requests"""
        
        # Create response tags
        tags = [
            Tag.parse(["e", original_event.id().to_hex()]),      # Reference original request
            Tag.parse(["p", original_event.author().to_hex()]),  # Tag the requester
            Tag.parse(["category", self.category]),               # Our service category
        ]
        
        if success:
            tags.append(Tag.parse(["status", "success"]))
        else:
            tags.append(Tag.parse(["status", "error"]))
        
        # Create the response event (same kind as request!)
        event_builder = EventBuilder(kind=Kind(25000), content=result)
        # Add tags using the tags method
        event_builder = event_builder.tags(tags)
        
        # Send the event
        await self.client.send_event_builder(event_builder)
        result_event = event_builder.build(self.keys.public_key())
        
        return result_event
```

Notice how clean this is - we use the same event kind but tag the original request with an "e" tag. The client can easily filter for responses to their specific requests.

### Heartbeat Events

You should publish a heartbeat event that tells people your DVM is online at regular intervals. A good interval is once every 5 minutes.

```json
{
	"kind": 11998,
	"pubkey": "<dvm-pubkey-generated-in-step-1>",
	"created_at": 1000000000, // this is what DVM marketplaces will use to decided whether your DVM is online or not
	"content": "<status_information>", // can be as simple as "online"
}
```

And here's what that looks like with our running python example:

```python
async def send_heartbeat(self):
"""Send periodic heartbeat to indicate DVM is online"""

	while True:
		try:
			# Create heartbeat event (kind 11998)
			event_builder = EventBuilder(kind=Kind(11998), content="online")
			await self.client.send_event_builder(event_builder)
			current_time = Timestamp.now()
			print(f"Sent heartbeat at {current_time.as_secs()}")
		except Exception as e:
			print(f"Error sending heartbeat: {e}")
			
			# Wait 10 seconds before next heartbeat (for testing)
			await asyncio.sleep(10)
```

That's all the code you need for a working DVM! The new approach makes it incredibly simple to build and deploy computational services on Nostr. Complete working examples can be found here: https://github.com/dtdannen/new-dvm-examples

## Step 6 of 6: Run Your DVM!

Unlike traditional APIs, DVMs offer incredible deployment flexibility - you can literally run one from your laptop. Only the relays see your IP address, giving you better privacy and freedom from traditional hosting requirements. Since we're using ephemeral events (kind 25000), relays won't store the events long-term. You MUST implement local storage to ensure you don't miss events. Remember that relays are transport, not storage. Always assume events can disappear at any time.

### A quick note on accepting payments
The payment landscape over Nostr is constantly innovating. The most common approach today is to generate a lightning payment invoice and include that in an intermediate response to a user's first request. Once the user pays, you do the work and send the final result. Libraries implementing Nostr Wallet Connect are an excellent place to start. 

An alternative is to ask the users to submit eCash with their request. Check out how [npub130mznv74rxs03…7ql29s](https://njump.me/npub130mznv74rxs032peqym6g3wqavh472623mt3z5w73xq9r6qqdufs7ql29s) does it with a more traditional API service. 

You can also offer a subscription, in which case make sure you give instructions in your documentation on how users can pay, and make sure you give a valid error response when a user's subscription isn't valid.

### Coming Soon: Encrypted DVMs

While this guide covers unencrypted DVMs, stay tuned for examples that implement end-to-end encryption using NIP-17/NIP-59 patterns. This will allow:
- Privacy of job requests and responses
- Hidden metadata about who is using which services
- Enhanced security for sensitive computational tasks

In the meantime, you can start building with these patterns - the encrypted version will use the same event kinds and basic structure, just with gift-wrapped events for privacy. Heartbeat events and announcements will remain unencrypted.
