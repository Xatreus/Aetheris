import {
  metrics,
  SpanStatusCode,
  trace,
  type Attributes,
} from "@opentelemetry/api";

const instrumentationVersion = "0.2.0";
const tracer = trace.getTracer("aetheris-sdk", instrumentationVersion);
const meter = metrics.getMeter("aetheris-sdk", instrumentationVersion);

const operationCount = meter.createCounter("aetheris.operations", {
  description: "Number of instrumented application operations",
});
const operationErrors = meter.createCounter("aetheris.operation.errors", {
  description: "Number of failed instrumented application operations",
});
const operationDuration = meter.createHistogram("aetheris.operation.duration", {
  description: "Duration of instrumented application operations",
  unit: "ms",
});

const sensitiveAttribute = /(prompt|completion|secret|password|token|authorization|email|phone|body)/i;

export interface ObserveOperationInput {
  service: string;
  version: string;
  environment?: string;
  operation: string;
  attributes?: Record<string, string | number | boolean>;
}

/** Record a trace and bounded-cardinality metrics around an async operation. */
export async function observeOperation<T>(
  input: ObserveOperationInput,
  operation: () => Promise<T>,
): Promise<T> {
  const startedAt = performance.now();
  const environment = input.environment ?? "development";
  const metricAttributes: Attributes = {
    "service.name": input.service,
    "deployment.environment": environment,
    "aetheris.operation": input.operation,
  };

  return tracer.startActiveSpan(`aetheris.${input.operation}`, async (span) => {
    const spanAttributes: Attributes = {
      ...metricAttributes,
      "service.version": input.version,
    };

    for (const [key, value] of Object.entries(input.attributes ?? {})) {
      if (!sensitiveAttribute.test(key)) {
        spanAttributes[`aetheris.${key}`] = value;
      }
    }

    span.setAttributes(spanAttributes);
    let failed = false;

    try {
      const result = await operation();
      span.setAttribute("aetheris.success", true);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      failed = true;
      span.setAttribute("aetheris.success", false);
      span.setAttribute(
        "aetheris.error_type",
        error instanceof Error ? error.name : "UnknownError",
      );
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      const durationMs = performance.now() - startedAt;
      span.setAttribute("aetheris.latency_ms", durationMs);
      operationCount.add(1, metricAttributes);
      operationDuration.record(durationMs, metricAttributes);
      if (failed) operationErrors.add(1, metricAttributes);
      span.end();
    }
  });
}
