import Navbar from "../components/home/HomeNavbar";
import Hero from "../components/home/Hero";
import BuiltFor from "../components/home/BuiltFor";
import Features from "../components/home/Features";
import Workflow from "../components/home/Workflow";
import WhyKritiq from "../components/home/WhyKritiq";
import CTA from "../components/home/CTA";
import Footer from "../components/home/Footer";

const Home = () => {
  return (
    <div className="min-h-screen overflow-x-hidden bg-[#0B1120] text-white">
      {/* Background Effects */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        {/* Top Glow */}
        <div className="absolute left-1/2 top-0 h-[550px] w-[550px] -translate-x-1/2 rounded-full bg-violet-600/20 blur-[140px]" />

        {/* Left Glow */}
        <div className="absolute left-0 top-1/3 h-[350px] w-[350px] rounded-full bg-cyan-500/10 blur-[130px]" />

        {/* Right Glow */}
        <div className="absolute right-0 bottom-20 h-[350px] w-[350px] rounded-full bg-fuchsia-600/10 blur-[130px]" />
      </div>

      {/* Navigation */}
      <Navbar />

      {/* Hero */}
      <Hero />

      {/* Technology Stack */}
      <BuiltFor />

      {/* Features */}
      <Features />

      {/* Workflow */}
      <Workflow />

      {/* Why KRITIQ */}
      <WhyKritiq />

      {/* Call To Action */}
      <CTA />

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Home;