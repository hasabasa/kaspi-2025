
import { useState } from "react";
import { Outlet } from "react-router-dom";
import AdminSidebar from "@/components/admin/AdminSidebar";
import AdminHeader from "@/components/admin/AdminHeader";
import { cn } from "@/lib/utils";
import { useScreenSize } from "@/hooks/use-screen-size";

const AdminLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { isMobile } = useScreenSize();

  const getMainMargin = () => {
    if (isMobile) return "ml-0";
    return sidebarOpen ? "ml-64" : "ml-16";
  };

  return (
    <div className="min-h-screen bg-red-50/30">
      <AdminSidebar 
        isOpen={sidebarOpen} 
        setIsOpen={setSidebarOpen}
      />
      
      <div className={cn(
        "transition-all duration-300 ease-in-out min-h-screen",
        getMainMargin()
      )}>
        <AdminHeader 
          toggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
          isMobile={isMobile}
        />
        <main className="p-6 min-h-[calc(100vh-80px)]">
          <div className="w-full max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
