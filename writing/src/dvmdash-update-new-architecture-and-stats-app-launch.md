---
title: DVMDash Update: New Architecture and Stats App Launch
date: 2025-02-14
summary: DVMDash is back with a completely rebuilt architecture, launching first with a new Stats app that provides flexible time-based metrics and network activity visualization for the DVM ecosystem. This update marks the first phase of a larger redesign that will soon bring back debugging tools and add a new playground for DVM interaction.
slug: dvmdash-update-new-architecture-and-stats-app-launch
tags: dvm, rundvm, ai, decentralized-ai
headerImage: assets/writing/dvmdash-update-new-architecture-and-stats-app-launch-header.webp
nostrEvent: 48d99de58d451632b5b9657573215df47674cd2d87a59beb3f7c7e4a80f618f3
nostrDtag: 1739508102538
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
I'm excited to share the first phase of DVMDash's major redesign! After some recent downtime issues (thanks [npub1e5tfhk8m65teu…ct7mh9](https://njump.me/npub1e5tfhk8m65teu25dfx8lcvwn4c8ypqjl72u2sh4rt8zy2kss0j5qct7mh9) and [npub1jlrs53pkdfjnt…djynqn](https://njump.me/npub1jlrs53pkdfjnts29kveljul2sm0actt6n8dxrrzqcersttvcuv3qdjynqn) for the heads up), I've been working on rebuilding DVMDash from the ground up to be more modular, scalable, and reliable.

## What's Live Now: The Stats App

The first piece of the new DVMDash is our completely rebuilt Stats app. Instead of trying to do everything at once, we're now breaking DVMDash into focused tools. The Stats app brings:

- Flexible time windows (1h, 24h, 7d, 30d) for more relevant insights
- Bar graphs showing activity over time
- Per-DVM and per-Kind detailed metrics

For those interested in the new backend architecture, check out my [recent post about performance gains](nostr:naddr1qvzqqqr4gupzpkscaxrqqs8nhaynsahuz6c6jy4wtfhkl2x4zkwrmc4cyvaqmxz3qqxnzdenxu6nwd3sxgmryv3506t7ws) describing how horizontal scaling is needed to support the growing DVM ecosystem.


## Coming Soon: Debug Tools and Playground

You'll notice on the new [landing page](https://dvmdash.live) that DVMDash is now split into three main tools:

1. Stats (available now!)
2. Debug Tools (coming soon)
3. Data Vending Playground (coming soon)

The Debug Tools will bring back the interactive graph-based debugger and event browser, while the Playground will offer a space to experiment with DVMs directly. I'm focusing on getting these right rather than rushing them out.

## Running Locally

Want to try it out? You can clone the repository and run the Stats app locally with a simple 

```
docker compose --profile all up
```

then visit **localhost:3000** in your browser.

## What's Next

My immediate focus is on:

1. Polishing the Stats app with new features like:
   * Sortable tables for easier data analysis
   * Enhanced DVM profiles with pictures and metadata from relays
   * More detailed DVM-specific metrics
2. Bringing back the debugging tools
3. Building out the playground

This is very much a work in progress, and I appreciate your patience as we rebuild. If you run into any issues or have suggestions, please drop by our GitHub repository.
