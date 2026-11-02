import {startSightlineTelemetry,stopSightlineTelemetry} from "./telemetry.js";
import {observeOperation} from "./index.js";
startSightlineTelemetry();
try {const result=await observeOperation({service:"sample-agent",version:"0.1.0",operation:"retrieve_context",attributes:{provider:"demo",region:"local"}},async()=>{await new Promise(r=>setTimeout(r,40));return {retrievedDocuments:3};}); console.log("Synthetic operation completed",result);} finally {await stopSightlineTelemetry();}
