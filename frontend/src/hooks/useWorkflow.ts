import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createWorkflow,
  getWorkflowStatus,
  stopWorkflow,
  WorkflowConfig,
  WorkflowStatusResponse,
  WorkflowStatus,
} from '../services/api';

export const useWorkflow = () => {
  const queryClient = useQueryClient();
  const [activeWorkflowId, setActiveWorkflowId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll workflow status
  const { data: workflowData, isLoading } = useQuery({
    queryKey: ['workflow', activeWorkflowId],
    queryFn: () => getWorkflowStatus(activeWorkflowId!),
    enabled: !!activeWorkflowId && (
      !workflowData?.status ||
      workflowData.status === WorkflowStatus.PENDING ||
      workflowData.status === WorkflowStatus.RUNNING
    ),
    refetchInterval: 1000, // Poll every second
    retry: false,
  });

  // Create workflow mutation
  const createMutation = useMutation({
    mutationFn: (config: WorkflowConfig) => createWorkflow(config),
    onSuccess: (data) => {
      setActiveWorkflowId(data.workflow_id);
      setError(null);
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to create workflow');
    },
  });

  // Stop workflow mutation
  const stopMutation = useMutation({
    mutationFn: () => stopWorkflow(activeWorkflowId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow', activeWorkflowId] });
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to stop workflow');
    },
  });

  const createWorkflowHandler = (config: WorkflowConfig) => {
    createMutation.mutate(config);
  };

  const stopWorkflowHandler = () => {
    if (activeWorkflowId) {
      stopMutation.mutate();
    }
  };

  // Auto-reset active workflow when completed/failed/stopped
  if (workflowData?.status === WorkflowStatus.COMPLETED ||
      workflowData?.status === WorkflowStatus.FAILED ||
      workflowData?.status === WorkflowStatus.STOPPED) {
    // Keep activeWorkflowId for result viewing, don't auto-reset
  }

  return {
    createWorkflow: createWorkflowHandler,
    stopWorkflow: stopWorkflowHandler,
    workflowData,
    activeWorkflowId,
    isLoading,
    error,
    isCreating: createMutation.isPending,
    isStopping: stopMutation.isPending,
  };
};
