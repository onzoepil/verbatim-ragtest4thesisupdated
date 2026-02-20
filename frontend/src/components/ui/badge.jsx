import React from "react";

export function Badge({ children, className = "", ...props }) {
  const classes =
    "inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700 " +
    className;

  return (
    <span className={classes} {...props}>
      {children}
    </span>
  );
}
