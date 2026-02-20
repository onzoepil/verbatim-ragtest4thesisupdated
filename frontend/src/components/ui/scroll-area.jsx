import React from "react";

export function ScrollArea({ children, className = "", ...props }) {
  const classes = "relative max-h-full overflow-y-auto " + className;
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
}
