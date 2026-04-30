// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// --8<-- [start:tool]
import { FunctionTool } from '@google/adk';
import { z } from 'zod';

const fetchItems = async (id: string) => ['item1', 'item2', 'item3'];
const processItem = async (item: string) => ({ processed: item });

const longRunningTool = new FunctionTool({
  name: 'process_data',
  description: 'Processes data in multiple steps.',
  parameters: z.object({
    dataId: z.string(),
  }),
  execute: async (args, toolContext) => {
    const items = await fetchItems(args.dataId);

    const results = [];
    for (const item of items) {
      // Check the abort signal before each step
      if (toolContext?.abortSignal?.aborted) {
        return { status: 'cancelled', processed: results.length };
      }

      results.push(await processItem(item));
    }

    return { status: 'complete', processed: results.length };
  },
});
// --8<-- [end:tool]
