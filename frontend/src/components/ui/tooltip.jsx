import React from "react";

export function TooltipProvider({ children }) {
  return <>{children}</>;
}

export function Tooltip({ children }) {
  return <>{children}</>;
}

export function TooltipTrigger({ children, className = "", ...props }) {
  return (
    <span className={className} {...props}>
      {children}
    </span>
  );
}

export function TooltipContent({ children, className = "", ...props }) {
  return (
    <span className={className} {...props}>
      {children}
    </span>
  );
}
