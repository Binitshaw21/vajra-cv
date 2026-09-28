from pathlib import Path


def test_kubernetes_manifest_exists():
    manifest = Path('k8s/deployment.yaml')
    assert manifest.exists()
    content = manifest.read_text(encoding='utf-8')
    assert 'Deployment' in content
    assert 'Service' in content
    assert 'vajra-backend' in content


def test_readme_describes_deployable_platform():
    readme = Path('README.md').read_text(encoding='utf-8')
    assert 'Production architecture' in readme
    assert 'Docker' in readme
    assert 'Kubernetes' in readme
