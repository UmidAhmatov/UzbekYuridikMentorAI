import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

import type { Language } from "../i18n";
import { t } from "../i18n";

type ErrorBoundaryProps = {
  children: ReactNode;
  language: Language;
};

type ErrorBoundaryState = {
  failed: boolean;
};

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("UI error boundary", error, info);
  }

  componentDidUpdate(previousProps: ErrorBoundaryProps) {
    if (previousProps.language !== this.props.language && this.state.failed) {
      this.setState({ failed: false });
    }
  }

  render() {
    if (this.state.failed) {
      return (
        <div role="alert" style={{ padding: 24 }}>
          <p>{t(this.props.language, "unexpectedError")}</p>
          <button onClick={() => this.setState({ failed: false })} type="button">
            {t(this.props.language, "retry")}
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

