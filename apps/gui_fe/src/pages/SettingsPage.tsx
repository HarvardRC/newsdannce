// TOOD: finish settings page

import { delete_verb, postFormDataFile } from '@/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useSkeletonPath } from '@/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

export default function SettingsPage() {
  const [file, setFile] = useState<File | null>(null);

  const queryClient = useQueryClient();

  const { data: skeletonPath, isLoading: isSkeletonPathLoading } =
    useSkeletonPath();

  if (isSkeletonPathLoading) {
    return <div>Loading...</div>;
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUploadSkeleton = async () => {
    if (!file) {
      console.log('File not provided');
      return;
    }
    try {
      const result = await postFormDataFile('/settings_page/skeleton', file);
      console.log('RESULT:', result);
    } catch (e) {
      console.error('Error uploading', e);
    }
    queryClient.invalidateQueries({ queryKey: ['skeletonPath'] });
  };

  const handleDeleteSkeleton = async () => {
    try {
      const result = await delete_verb('/settings_page/skeleton');
      console.log('RESULT:', result);
    } catch (e) {
      console.error('Error deleting', e);
    }
    queryClient.invalidateQueries({ queryKey: ['skeletonPath'] });
  };

  return (
    <>
      <h1 className="text-2xl font-bold mb-4">App Settings</h1>
      <h2 className="text-xl font-semibold mb-1">Dannce Skeleton</h2>
      <p>
        This should be a .mat file containing dannce joints and joint names.
        E.g. from <pre className="inline">label3d/skeletons</pre> folder.
      </p>
      <div>
        {' '}
        <b>Current skeleton:</b>{' '}
        {skeletonPath!.data == null ? 'None' : skeletonPath!.data}{' '}
      </div>

      <div className="grid w-full max-w-xs items-center gap-1.5">
        <Label htmlFor="selectSkeleton">Select skeleton</Label>
        <Input
          className="cursor-pointer"
          id="selectSkeleton"
          onChange={handleFileChange}
          type="file"
        />
        <Button type="button" disabled={!file} onClick={handleUploadSkeleton}>
          Use This Skeleton
        </Button>
        <Button
          type="button"
          variant="destructive"
          onClick={handleDeleteSkeleton}
          disabled={!skeletonPath!.data}
        >
          Delete Skeleton
        </Button>
      </div>
    </>
  );
}
