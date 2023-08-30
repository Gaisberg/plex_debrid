The idea behind this was to make a simple and functional rewrite of plex debrid that seemed to get a bit clustered.

Rewrite of plex_debrid project, limited functionality:
- Services include: plex, mdblist, torrentio and realdebrid

TODO:
- Real-debrid should download only one file per stream, lets avoid collections
- Implement uncached download in real-rebrid
- Add overseerr support
- Modify scraping logic to try scaping once a day if not found?
- Check real-debrid for content at startup, we dont want duplicates!
- Add support for shows
- Improve logging...
