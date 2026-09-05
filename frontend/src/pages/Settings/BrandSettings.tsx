import { AlertCircle, CheckCircle2, Palette } from "lucide-react";
import { useEffect, useState } from "react";

import { extractErrorMessage } from "../../api/client";
import { getBrandProfile, saveBrandProfile } from "../../api/workspaces";
import { Button } from "../../components/ui/Button";
import { Card, CardBody, CardHeader } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { HelperText, Input, Label } from "../../components/ui/Input";
import { Spinner } from "../../components/ui/Spinner";
import { TagInput } from "../../components/ui/TagInput";
import { useWorkspace } from "../../hooks/useWorkspace";
import type { BrandProfile } from "../../types";

const EMPTY_PROFILE: BrandProfile = {
  brand_name: "",
  description: "",
  website: "",
  industry: "",
  target_audience: [],
  target_countries: [],
  target_languages: [],
  brand_tone: "",
  brand_keywords: [],
  forbidden_words: [],
  cta_style: "",
  preferred_hashtags: [],
  logo_url: "",
  brand_colors: [],
};

export function BrandSettings() {
  const { currentWorkspace } = useWorkspace();
  const [profile, setProfile] = useState<BrandProfile>(EMPTY_PROFILE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentWorkspace) return;
    setLoading(true);
    getBrandProfile(currentWorkspace.id)
      .then((data) => setProfile(data ?? { ...EMPTY_PROFILE, brand_name: currentWorkspace.name }))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [currentWorkspace]);

  if (!currentWorkspace) {
    return (
      <EmptyState
        icon={<Palette className="h-6 w-6" />}
        title="No workspace yet"
        description="Create a workspace from the Dashboard first, then come back to set up its brand profile."
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-16 text-sm text-slate-400">
        <Spinner className="h-4 w-4" />
        Loading brand profile...
      </div>
    );
  }

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const saved = await saveBrandProfile(currentWorkspace.id, profile);
      setProfile(saved);
      setMessage("Brand profile saved.");
    } catch (err) {
      setError(extractErrorMessage(err, "Could not save brand profile."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6 pb-24">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Brand Profile</h1>
        <p className="mt-1 text-sm text-slate-500">
          The AI content pipeline uses this whenever it generates or scores content for{" "}
          <span className="font-medium text-slate-700">{currentWorkspace.name}</span>.
        </p>
      </div>

      <Card>
        <CardHeader title="Identity" description="Who this brand is and where it operates." />
        <CardBody className="space-y-4">
          <div>
            <Label>Brand name</Label>
            <Input
              value={profile.brand_name}
              onChange={(e) => setProfile({ ...profile, brand_name: e.target.value })}
            />
          </div>
          <div>
            <Label>Description</Label>
            <textarea
              value={profile.description ?? ""}
              onChange={(e) => setProfile({ ...profile, description: e.target.value })}
              rows={3}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-xs transition-colors placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Label>Website</Label>
              <Input
                value={profile.website ?? ""}
                onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                placeholder="https://"
              />
            </div>
            <div>
              <Label>Industry</Label>
              <Input
                value={profile.industry ?? ""}
                onChange={(e) => setProfile({ ...profile, industry: e.target.value })}
                placeholder="Education / Technology"
              />
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Audience & reach" description="Who the content should speak to." />
        <CardBody className="space-y-4">
          <div>
            <Label>Target audience</Label>
            <TagInput
              value={profile.target_audience}
              onChange={(v) => setProfile({ ...profile, target_audience: v })}
              placeholder="Final-year students, aspiring developers..."
            />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Label>Target countries</Label>
              <TagInput
                value={profile.target_countries}
                onChange={(v) => setProfile({ ...profile, target_countries: v })}
                placeholder="India, United States..."
              />
            </div>
            <div>
              <Label>Target languages</Label>
              <TagInput
                value={profile.target_languages}
                onChange={(v) => setProfile({ ...profile, target_languages: v })}
                placeholder="English, Hindi..."
              />
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Voice & content rules" description="Guardrails the AI content pipeline must respect." />
        <CardBody className="space-y-4">
          <div>
            <Label>Brand tone</Label>
            <Input
              value={profile.brand_tone ?? ""}
              onChange={(e) => setProfile({ ...profile, brand_tone: e.target.value })}
              placeholder="Friendly, expert, encouraging"
            />
          </div>
          <div>
            <Label>Brand keywords</Label>
            <TagInput
              value={profile.brand_keywords}
              onChange={(v) => setProfile({ ...profile, brand_keywords: v })}
              placeholder="Python, FastAPI, React, AI..."
            />
          </div>
          <div>
            <Label>Forbidden words</Label>
            <TagInput
              value={profile.forbidden_words}
              onChange={(v) => setProfile({ ...profile, forbidden_words: v })}
              placeholder="guaranteed job, #1..."
            />
            <HelperText>The quality agent (Phase 2) blocks these from published content.</HelperText>
          </div>
          <div>
            <Label>Preferred hashtags</Label>
            <TagInput
              value={profile.preferred_hashtags}
              onChange={(v) => setProfile({ ...profile, preferred_hashtags: v })}
              placeholder="#AI, #Python, #StudentDevelopers..."
            />
          </div>
          <div>
            <Label>CTA style</Label>
            <Input
              value={profile.cta_style ?? ""}
              onChange={(e) => setProfile({ ...profile, cta_style: e.target.value })}
              placeholder="e.g. Direct, ask a question, link in bio"
            />
          </div>
        </CardBody>
      </Card>

      {message && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4 flex-none" />
          {message}
        </div>
      )}
      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          <AlertCircle className="mt-0.5 h-4 w-4 flex-none" />
          {error}
        </div>
      )}

      {/* Sticky save bar so the action stays reachable on long forms / small screens */}
      <div className="fixed inset-x-0 bottom-0 z-10 border-t border-slate-200 bg-white/90 px-4 py-3 backdrop-blur lg:left-72">
        <div className="mx-auto flex max-w-3xl items-center justify-end gap-3 sm:px-6 lg:px-8">
          <Button onClick={handleSave} loading={saving}>
            {saving ? "Saving..." : "Save brand profile"}
          </Button>
        </div>
      </div>
    </div>
  );
}
