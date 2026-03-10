import { NavbarNav } from "@/components/web/navbar-nav";
import { ReactNode } from "react";

export default function SharedLayout({children}: {children: ReactNode}) {
  return (
    <>
      <NavbarNav />
      {children}
    </>
  );
}
