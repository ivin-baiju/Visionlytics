import { Queue } from "bullmq";

export interface AnalysisJobPayload {
  analysisId: string;
  orgId: string;
  projectId: string;
  mediaId: string;
  storageKey: string;
  config: Record<string, unknown>;
}

export interface TrainingJobPayload {
  trainingRunId: string;
  orgId: string;
  datasetId: string;
  baseArchitecture: string;
  preset: "fast" | "balanced" | "max_accuracy";
}

export interface JobQueues {
  analysis: Queue<AnalysisJobPayload>;
  training: Queue<TrainingJobPayload>;
  deadLetter: Queue<Record<string, unknown>>;
  close: () => Promise<void>;
}

export function createJobQueues(redisUrl: string): JobQueues {
  const url = new URL(redisUrl);
  const connection = {
    host: url.hostname,
    port: Number(url.port || 6379),
    maxRetriesPerRequest: null,
  };

  const defaultJobOptions = {
    attempts: 3,
    backoff: {
      type: "exponential" as const,
      delay: 1500,
    },
    removeOnComplete: 500,
    removeOnFail: 1000,
  };

  const analysis = new Queue<AnalysisJobPayload>("visionlytics-analysis", {
    connection,
    defaultJobOptions,
  });

  const training = new Queue<TrainingJobPayload>("visionlytics-training", {
    connection,
    defaultJobOptions,
  });

  const deadLetter = new Queue<Record<string, unknown>>("visionlytics-dlq", {
    connection,
  });

  return {
    analysis,
    training,
    deadLetter,
    close: async () => {
      await Promise.allSettled([analysis.close(), training.close(), deadLetter.close()]);
    },
  };
}
