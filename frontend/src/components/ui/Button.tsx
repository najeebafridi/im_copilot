import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-xl border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60",
  {
    variants: {
      variant: {
        primary: "border-transparent text-white",
        secondary: "border-transparent text-white",
        outline: "bg-transparent",
        danger: "border-transparent text-white",
      },
      size: {
        default: "h-11",
        sm: "h-9 px-3 text-sm",
        lg: "h-12 px-5 text-base",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    loading?: boolean;
  };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading = false, disabled, children, ...props }, ref) => {
    const isDisabled = disabled || loading;
    const variantStyle = {
      primary: { backgroundColor: "#16324F", color: "#FFFFFF" },
      secondary: { backgroundColor: "#415A77", color: "#FFFFFF" },
      outline: { borderColor: "#D7DEE8", color: "#10243B", backgroundColor: "#FFFFFF" },
      danger: { backgroundColor: "#B42318", color: "#FFFFFF" },
    }[variant ?? "primary"];

    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        style={variantStyle}
        disabled={isDisabled}
        {...props}
      >
        {loading ? "Loading..." : children}
      </button>
    );
  },
);

Button.displayName = "Button";
