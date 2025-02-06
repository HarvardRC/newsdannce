// TOOD: finish settings page

import { delete_verb, post, postFormDataFile } from '@/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useSkeletonPath } from '@/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { FormEvent, useRef, useState } from 'react';

export default function SettingsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sqlResponse, setSqlResponse] = useState<string | null>(null);

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

  const handleRunCommand = async (e: any) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const sql = formData.get('sqlCommand');
    console.log('SQL IS ', formData.get('sqlCommand'));
    const response = await post('/admin/execute_sql', {
      sql: sql,
    });

    setSqlResponse(JSON.stringify(response, null, 2));

    console.log('RESPONSE IS ', response);
  };

  return (
    <>
      <h1 className="text-2xl font-bold mb-4">App Settings</h1>
      <h2 className="text-xl font-semibold mb-1">Dannce Skeleton</h2>
      <p>
        This should be a .mat file containing dannce joints and joint names.
        E.g. from <span className="inline font-mono">label3d/skeletons</span>{' '}
        folder.
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
      <h2 className="text-xl font-semibold mb-0 mt-6">
        Database Commands [Advanced]
      </h2>
      <div>Don't use unless you know what you're doing!</div>
      <form onSubmit={handleRunCommand}>
        <textarea
          name="sqlCommand"
          className="w-full border border-gray-400 rounded-sm p-1 h-40"
        />
        <Button type="submit" className="w-80 mt-4">
          Run Command
        </Button>
      </form>
      <div>
        <pre> {sqlResponse} </pre>
      </div>
    </>
  );
}
