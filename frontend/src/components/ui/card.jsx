import React from "react";

export function Card({ children, className = "", ...props }) {
  return (
    <div
      className={
        "rounded-lg border border-gray-200 bg-white shadow-sm " + className
      }
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "", ...props }) {
  return (
    <div className={"border-b border-gray-100 px-4 py-2 " + className} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = "", ...props }) {
  return (
    <h2 className={"text-lg font-semibold " + className} {...props}>
      {children}
    </h2>
  );
}

export function CardContent({ children, className = "", ...props }) {
  return (
    <div className={"px-4 py-3 " + className} {...props}>
      {children}
    </div>
  );
}
