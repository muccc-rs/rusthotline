// First display calling and called party numbers
Engine.output("Got call from '" + message.caller + "' to '" + message.called + "'");


Channel.callJust("external/nodata/main.py");
// if (message.called.substr(0,2)=="19") {
//         // route calls starting with 19 to 192.168.168.1
//         // 5060 is the default SIP port. When using the default port you don't need to specify it
//         Channel.callJust("sip/sip:" + message.called + "@192.168.168.1:5060");

// } else if (message.called.substr(0,2)=="00" && message.called.length>10) {
//         //route calls using a function 
//         routeOutside();

// } else if (message.called.match("^60")) {
//         //route calls starting with 60 to 192.168.168.1
//         Channel.callJust("h323/" + message.called + "@192.168.168.1:1720");

// } else if (message.caller=="209") {
//         //route calls from caller: 209
//         Channel.callJust("iax/user_iax@192.168.168.1:4569/" + message.called + "@iaxcontext");

// } else {
//         //route other calls that don't match the above rules 
//         Channel.callJust("wave/play//var/spool/sounds/hello.au");
// }

// function routeOutside() {
    
//     // rewrite caller number for all calls that will be routed to this account
//     message.caller = "+40211231234";

//     // rewrite called number: strip 00 and add +_in front of the number
//     message.called = "+" + message.called.substr(2);

//     // send all calls starting with +40 to line "gwout" defined in accfile.conf
//     if(message.called.substr(3) == "+40")        // alternative: if(message.called.match("^\+40.*"))
//     {
//          message.line = "gwout";
//     }
//     Channel.callJust("line/" + message.called);
// }