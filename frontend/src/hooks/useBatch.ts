import { useMutation, useQuery } from '@tanstack/react-query';
import { startBatch, getBatchStatus, stopBatch } from '../services/api';
import type { BatchRequest, BatchStatus } from '../services/api';
import { useState } from 'react';

export const useBatch = () => {
  const [currentBatchId, setCurrentBatchId] = useState<string | null>(null);

  const startMutation = useMutation({
    mutationKey: ['startBatch'],
    mutationFn: (config: BatchRequest) => startBatch(config),
    onSuccess: (_, variables) => {
      setCurrentBatchId(variables.batch_id);
    },
  });

  const stopMutation = useMutation({
    mutationKey: ['stopBatch'],
    mutationFn: (id: string) => stopBatch(id),
  });

  const batchQuery = useQuery<BatchStatus>({
    queryKey: ['batch', currentBatchId],
    queryFn: () => getBatchStatus(currentBatchId!),
    enabled: !!currentBatchId,
    refetchInterval: (query) => {
       const status = query.state.data?.status;
       if (status === 'running' || status === 'pending') {
         return 1000;
       }
       return false;
    },
  });

  return {
    startBatch: startMutation.mutate,
    isStarting: startMutation.isPending,
    stopBatch: stopMutation.mutate,
    isStopping: stopMutation.isPending,
    batchData: batchQuery.data,
    isLoading: batchQuery.isLoading,
    currentBatchId,
  };
};
