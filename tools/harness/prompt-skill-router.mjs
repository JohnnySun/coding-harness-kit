#!/usr/bin/env node
// Thin in-repo entrypoint. The portable advisory runtime lives with the
// profile SSOT so subject export and this repository execute the same logic.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  analyzePromptSkillContext,
  buildAdditionalContext,
  buildHookResponse,
  main,
  selectPromptSkills,
  skillCatalog,
} from '../../agent-kit/profile/agent-profile-router.mjs';

export {
  analyzePromptSkillContext,
  buildAdditionalContext,
  buildHookResponse,
  selectPromptSkills,
  skillCatalog,
};

const isMain = process.argv[1]
  && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  main().catch((error) => {
    process.stderr.write(`prompt router advisory failed open: ${error.message}\n`);
    process.stdout.write('{}\n');
    process.exitCode = 0;
  });
}
