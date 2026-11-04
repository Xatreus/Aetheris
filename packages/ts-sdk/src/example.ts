import { observeOperation } from "./index.js";
import { startAetherisTelemetry, stopAetherisTelemetry } from "./telemetry.js";

startAetherisTelemetry();

try {
  const result = await observeOperation(
    {
      service: "sample-agent",
      version: "0.2.0",
      operation: "retrieve_context",
      attributes: { provider: "demo", region: "local" },
    },
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 40));
      return { retrievedDocuments: 3 };
    },
  );
  console.log("Synthetic operation completed", result);
} finally {
  await stopAetherisTelemetry();
}
