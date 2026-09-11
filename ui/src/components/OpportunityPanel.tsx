import { useState } from 'react';
import { CheckCircle2, ClipboardList, ExternalLink, Loader2, ShieldCheck } from 'lucide-react';
import type { OpportunityAssessment, TaskDraft } from '../types';

type OpportunityPanelProps = {
  assessment: OpportunityAssessment;
  leadId: string | null;
  apiUrl: string;
  glassStyle: string;
};

const scoreTone = (value: number) => {
  if (value >= 16) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
  if (value >= 10) return 'text-amber-700 bg-amber-50 border-amber-200';
  return 'text-rose-700 bg-rose-50 border-rose-200';
};

const OpportunityPanel = ({ assessment, leadId, apiUrl, glassStyle }: OpportunityPanelProps) => {
  const [tasks, setTasks] = useState<TaskDraft[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [message, setMessage] = useState('');

  const createDrafts = async () => {
    if (!leadId || isCreating) return;
    setIsCreating(true);
    setMessage('');
    try {
      const response = await fetch(`${apiUrl}/leads/${leadId}/task-drafts`, { method: 'POST' });
      if (!response.ok) throw new Error('任务草稿生成失败');
      const data = await response.json();
      setTasks(data.items || []);
      setMessage('任务草稿已生成，外部同步仍需人工批准。');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : '任务草稿生成失败');
    } finally {
      setIsCreating(false);
    }
  };

  const approveTask = async (taskId: number) => {
    const response = await fetch(`${apiUrl}/task-drafts/${taskId}/approve`, { method: 'POST' });
    if (!response.ok) {
      setMessage('任务批准失败');
      return;
    }
    const data = await response.json();
    setTasks((current) => current.map((task) => task.id === taskId ? { ...task, status: data.task.status } : task));
    setMessage('任务已批准为本地待办，尚未伪造飞书同步。');
  };

  const score = assessment.score;
  return (
    <section className={`${glassStyle} p-6 space-y-6`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">Opportunity Decision</p>
          <h2 className="mt-1 text-2xl font-semibold text-gray-900">客户机会与 Agent 方案</h2>
          <p className="mt-2 max-w-3xl text-gray-700">{assessment.executive_summary}</p>
        </div>
        <div className="min-w-28 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-center">
          <div className="text-3xl font-bold text-gray-900">{score.total}<span className="text-sm font-normal text-gray-500">/100</span></div>
          <div className="text-xs text-gray-500">机会总分</div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {[
          ['需求匹配', score.need_fit],
          ['业务价值', score.business_value],
          ['紧迫性', score.urgency],
          ['交付可行性', score.delivery_feasibility],
          ['证据质量', score.evidence_quality],
        ].map(([label, value]) => (
          <div key={label} className={`rounded-lg border px-3 py-2 ${scoreTone(Number(value))}`}>
            <div className="text-xs opacity-80">{label}</div>
            <div className="mt-1 text-xl font-semibold">{value}<span className="text-xs font-normal">/20</span></div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-lg font-semibold text-gray-900">识别出的客户痛点</h3>
          <div className="space-y-3">
            {assessment.pain_points.map((point, index) => (
              <article key={`${point.title}-${index}`} className="rounded-lg border border-gray-200 bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <h4 className="font-semibold text-gray-900">{point.title}</h4>
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">{point.priority}</span>
                </div>
                <p className="mt-2 text-sm leading-6 text-gray-700">{point.description}</p>
                {point.evidence.length > 0 && (
                  <div className="mt-3 space-y-2 border-t border-gray-100 pt-3">
                    {point.evidence.map((evidence, evidenceIndex) => (
                      <div key={evidenceIndex} className="text-xs text-gray-600">
                        <span>{evidence.claim}（置信度 {Math.round(evidence.confidence * 100)}%）</span>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {evidence.source_urls.map((url) => <a key={url} href={url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-blue-600 hover:underline"><ExternalLink className="h-3 w-3" />来源</a>)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-lg font-semibold text-gray-900">推荐 Agent 方案</h3>
          <div className="space-y-3">
            {assessment.recommended_solutions.map((solution, index) => (
              <article key={`${solution.name}-${index}`} className="rounded-lg border border-blue-100 bg-blue-50/50 p-4">
                <h4 className="font-semibold text-gray-900">{solution.name}</h4>
                <p className="mt-2 text-sm text-gray-700">{solution.target_problem}</p>
                <ol className="mt-3 list-decimal space-y-1 pl-5 text-sm text-gray-700">
                  {solution.workflow.map((step, stepIndex) => <li key={stepIndex}>{step}</li>)}
                </ol>
                <p className="mt-3 text-sm text-gray-700"><strong>预期价值：</strong>{solution.expected_value}</p>
                {solution.human_approval_points.length > 0 && <p className="mt-2 text-sm text-amber-800"><strong>人工审批：</strong>{solution.human_approval_points.join('；')}</p>}
              </article>
            ))}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 border-t border-gray-200 pt-5">
        <button type="button" onClick={createDrafts} disabled={!leadId || isCreating} className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50">
          {isCreating ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardList className="h-4 w-4" />}
          生成跟进任务草稿
        </button>
        <span className="inline-flex items-center gap-1 text-xs text-gray-500"><ShieldCheck className="h-4 w-4" />外部写操作必须人工确认</span>
        {message && <span className="text-sm text-gray-600">{message}</span>}
      </div>

      {tasks.length > 0 && <div className="space-y-2 rounded-lg border border-gray-200 bg-gray-50 p-4">
        <h3 className="font-semibold text-gray-900">待审批任务</h3>
        {tasks.map((task) => <div key={task.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md bg-white p-3">
          <div><div className="font-medium text-gray-900">{task.title}</div><div className="text-xs text-gray-500">{task.status === 'approved' ? '已批准' : '等待人工批准'}</div></div>
          {task.status === 'approved' ? <CheckCircle2 className="h-5 w-5 text-emerald-600" /> : <button type="button" onClick={() => approveTask(task.id)} className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">批准为本地待办</button>}
        </div>)}
      </div>}
    </section>
  );
};

export default OpportunityPanel;
