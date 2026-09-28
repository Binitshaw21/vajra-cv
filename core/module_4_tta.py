import torch
import torch.nn as nn
import torch.optim as optim

class SelfHealingTTA:
    """
    Test-Time Entropy Minimization (TENT). 
    Adapts the model to environmental drift (fog/sand) on-the-fly at the edge.
    """
    def __init__(self, model: nn.Module, lr: float = 0.001):
        self.model = model
        self.lr = lr
        self.optimizer = self._configure_tent_optimizer()

    def _configure_tent_optimizer(self):
        """Freezes all layers except BatchNorm parameters for self-healing."""
        self.model.train() # BN requires train mode to update statistics
        params_to_update = []
        for name, param in self.model.named_parameters():
            if 'bn' in name or 'batchnorm' in name.lower():
                param.requires_grad = True
                params_to_update.append(param)
            else:
                param.requires_grad = False
                
        if not params_to_update:
            for param in self.model.parameters():
                param.requires_grad = True
                params_to_update.append(param)
        return optim.Adam(params_to_update, lr=self.lr)

    def compute_entropy(self, logits: torch.Tensor) -> torch.Tensor:
        """Calculates Shannon entropy of the predictions."""
        probs = torch.softmax(logits, dim=-1)
        log_probs = torch.log_softmax(logits, dim=-1)
        entropy = -(probs * log_probs).sum(dim=-1)
        return entropy.mean()

    def adapt_to_environment(self, ood_batch: torch.Tensor, steps: int = 3) -> dict:
        """Runs the self-healing loop on the incoming drifted data."""
        initial_entropy = 0.0
        final_entropy = 0.0
        
        for step in range(steps):
            self.optimizer.zero_grad()
            logits = self.model(ood_batch)
            
            loss = self.compute_entropy(logits)
            if step == 0: initial_entropy = loss.item()
            
            loss.backward()
            self.optimizer.step()
            final_entropy = loss.item()

        self.model.eval() # Return to inference mode
        
        return {
            "status": "SELF_HEALING_COMPLETE",
            "initial_entropy": round(initial_entropy, 4),
            "final_entropy": round(final_entropy, 4),
            "adaptation_improvement": round(initial_entropy - final_entropy, 4)
        }