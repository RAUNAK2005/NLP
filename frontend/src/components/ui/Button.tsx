import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export default function Button({ children, className = "", variant = "primary", ...props }: PropsWithChildren<ButtonProps>) {
  const variants = {
    primary: "bg-accent text-white hover:bg-[#0b5f59]",
    secondary: "border border-line bg-white text-ink hover:bg-[#f4f7f9]",
    ghost: "text-accent hover:bg-[#e9f5f3]",
  };
  return (
    <button
      className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

