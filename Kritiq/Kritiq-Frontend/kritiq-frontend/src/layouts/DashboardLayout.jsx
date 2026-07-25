import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import NavBar from "../components/NavBar";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-[#101419] overflow-hidden">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <NavBar />

        <main className="flex-1 overflow-y-auto bg-[#101419] p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}