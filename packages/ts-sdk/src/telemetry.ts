import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
let sdk:NodeSDK|undefined;
export function startSightlineTelemetry():void {if(sdk)return; sdk=new NodeSDK({traceExporter:new OTLPTraceExporter({url:process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT??"http://localhost:4318/v1/traces"}),instrumentations:[getNodeAutoInstrumentations()]}); sdk.start();}
export async function stopSightlineTelemetry():Promise<void>{if(sdk){await sdk.shutdown();sdk=undefined;}}
