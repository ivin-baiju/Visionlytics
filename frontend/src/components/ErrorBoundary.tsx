"use client";

import React, { Component, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackMessage?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[Visionlytics Error Boundary]", error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="vl-error-boundary">
          <div className="vl-error-boundary-inner">
            <AlertTriangle size={36} color="var(--accent-rose)" />
            <h2>Something went wrong</h2>
            <p>
              {this.props.fallbackMessage || "An unexpected error occurred in this section."}
            </p>
            {this.state.error && (
              <code className="vl-error-boundary-code">
                {this.state.error.message}
              </code>
            )}
            <button
              type="button"
              className="vl-btn vl-btn-primary"
              onClick={this.handleRetry}
            >
              <RefreshCw size={16} /> Try Again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
