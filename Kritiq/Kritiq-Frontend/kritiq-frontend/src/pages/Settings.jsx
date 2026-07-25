import { useEffect, useState } from "react";
import axios from "axios";

import SettingsHeader from "../components/settings/SettingsHeader";
import ProfileCard from "../components/settings/ProfileCard";
import AccountInfo from "../components/settings/AccountInfo";
import { profile as initialProfile } from "../components/settings/settingsData";

const Settings = () => {
  const [profile, setProfile] = useState(initialProfile);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await axios.get("/profile");
        setProfile(data);
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  return (
    <div className="min-h-screen bg-[#0F172A] p-8">
      <SettingsHeader />

      <div className="mt-8 grid gap-8 lg:grid-cols-3">
        {/* Left */}
        <div>
          <ProfileCard profile={profile} />
        </div>

        {/* Right */}
        <div className="lg:col-span-2">
          {loading ? (
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 text-center text-zinc-400">
              Loading profile...
            </div>
          ) : (
            <AccountInfo profile={profile} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;