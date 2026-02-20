import React from "react";

export function Button({
  children,
  className = "",
  variant = "default",
  ...props
}) {
  const base =
    "inline-flex items-center justify-center rounded-md border text-sm font-medium px-3 py-1.5 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed";

  const variants = {
    default: "bg-blue-600 text-white border-transparent hover:bg-blue-700",
    outline: "bg-white text-gray-900 border-gray-300 hover:bg-gray-50",
    ghost: "bg-transparent border-transparent hover:bg-gray-100",
  };

  const classes = [base, variants[variant] || variants.default, className]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
