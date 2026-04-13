const { Repository } = require('@napi-rs/simple-git');
const readline = require('readline');

/**
 * Prompts the user in the terminal for an optional string to append.
 */
async function promptForMessage() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question('Additional sync info (optional string to append): ', (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function run() {
  try {
    // 1. Prompt for user input
    const extraInput = await promptForMessage();

    // 2. Open repository and find last commit
    const repo = Repository.discover(process.cwd());
    const headRef = repo.head().resolve();
    const lastCommit = repo.findCommit(headRef.target());

    if (!lastCommit) {
      throw new Error('No commit found to amend.');
    }

    // 3. Prepare the timestamp and message
    // Replaces the logic of %date% %time% with local JS strings
    const now = new Date();
    const timestamp = `(Quartz Sync: ${now.toLocaleDateString()} ${now.toLocaleTimeString()})`;
    
    const currentMessage = lastCommit.message() || '';
    const appendString = extraInput ? `${timestamp} ${extraInput}` : timestamp;
    const updatedMessage = `${currentMessage.trimEnd()}\n\n${appendString}`;

    // 4. Amend the commit (with a simple retry loop for Windows file locks)
    let attempts = 0;
    while (attempts < 3) {
      try {
        lastCommit.amend('HEAD', null, null, null, updatedMessage, null);
        console.log('Successfully updated commit message.');
        return;
      } catch (e) {
        attempts++;
        if (attempts === 3) throw e;
        console.warn(`Retry ${attempts}/3: Git index might be locked...`);
        await new Promise(r => setTimeout(r, 1000));
      }
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

run();