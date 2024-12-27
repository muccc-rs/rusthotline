// First display calling and called party numbers
Engine.output("Got call from '" + message.caller + "' to '" + message.called + "'");

if (message.called && message.called.length > 3 && (message.called.substr(0,4)=="8787"  || message.called.substr(0,4)=="7372")) {
    return Channel.callJust("external/nodata/main.py");
}

// The default behavior is to route the call to the requested line
