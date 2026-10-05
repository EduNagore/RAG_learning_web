import { useStore } from '@nanostores/react';
import { useEffect } from 'react';
import { $progress, hydrateProgress, markLessonRead, markLessonUnread } from '../../lib/progress';

export default function ReadToggle({ lessonId }: { lessonId: string }) {
  const progress = useStore($progress);
  useEffect(() => hydrateProgress(), []);
  const read = lessonId in progress.lessonsRead;

  return (
    <button
      type="button"
      aria-pressed={read}
      onClick={() => (read ? markLessonUnread(lessonId) : markLessonRead(lessonId))}
      className={
        read
          ? 'rounded-md border border-emerald-600 bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-100 dark:border-emerald-500 dark:bg-emerald-950 dark:text-emerald-200'
          : 'rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800'
      }
    >
      {read ? '✓ Lección leída' : 'Marcar como leída'}
    </button>
  );
}
