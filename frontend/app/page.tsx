import { redirect } from "next/navigation";

// Root page just redirects to /cars
export default function Home() {
  redirect("/cars");
}
