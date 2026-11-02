import { trace, SpanStatusCode, type Attributes } from "@opentelemetry/api";
const tracer = trace.getTracer("sightline-sdk", "0.1.0");
export async function observeOperation<T>(input: {service:string; version:string; environment?:string; operation:string; attributes?:Record<string,string|number|boolean>}, operation:()=>Promise<T>): Promise<T> {
 const start=performance.now(); return tracer.startActiveSpan(`sightline.${input.operation}`, async span=>{
  const attrs:Attributes={"service.name":input.service,"service.version":input.version,"deployment.environment":input.environment??"development","sightline.operation":input.operation};
  for(const [key,value] of Object.entries(input.attributes??{})){if(!/(prompt|completion|secret|password|token|authorization|email|phone|body)/i.test(key)) attrs[`sightline.${key}`]=value;}
  span.setAttributes(attrs); try {const result=await operation(); span.setAttribute("sightline.success",true); span.setStatus({code:SpanStatusCode.OK}); return result;}
  catch(error){span.setAttribute("sightline.success",false); span.setAttribute("sightline.error_type",error instanceof Error?error.name:"UnknownError"); span.setStatus({code:SpanStatusCode.ERROR}); throw error;}
  finally {span.setAttribute("sightline.latency_ms",performance.now()-start); span.end();}
 });
}
