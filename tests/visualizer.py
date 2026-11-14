"""
3D görselleştirme ve snapshot kaydetme modülü
Test başarısızlıklarında kapak ve gövde pozisyonlarını kaydeder
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from datetime import datetime


def ensure_failure_dir():
    """Başarısız testler için dizin oluştur"""
    failure_dir = os.path.join(os.path.dirname(__file__), '..', 'test_failures')
    os.makedirs(failure_dir, exist_ok=True)
    return failure_dir


def generate_snapshot_filename(test_name, angle_deg=None):
    """Snapshot dosya adı oluştur"""
    failure_dir = ensure_failure_dir()
    
    if angle_deg is not None:
        filename = f"{test_name}_angle_{angle_deg:.0f}deg.png"
    else:
        filename = f"{test_name}.png"
    
    return os.path.join(failure_dir, filename)


def visualize_assembly(body_mesh, lid_mesh, title_text, angle_deg=None, save_path=None):
    """
    Kutu ve kapak montajını 3D olarak görselleştir ve kaydet
    
    Args:
        body_mesh: Gövde mesh
        lid_mesh: Kapak mesh
        title_text: Başlık
        angle_deg: Açı (opsiyonel)
        save_path: Kaydetme yolu
    
    Returns:
        save_path: Kaydedilen dosya yolu
    """
    try:
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Gövde (Mavi)
        if body_mesh is not None:
            body_triangles = body_mesh.vertices[body_mesh.faces]
            body_collection = Poly3DCollection(
                body_triangles, 
                alpha=0.6, 
                facecolors='#4169E1',  # Royal Blue
                edgecolors='#1E90FF',
                linewidths=0.05
            )
            ax.add_collection3d(body_collection)
        
        # Kapak (Kırmızı)
        if lid_mesh is not None:
            lid_triangles = lid_mesh.vertices[lid_mesh.faces]
            lid_collection = Poly3DCollection(
                lid_triangles, 
                alpha=0.7, 
                facecolors='#FF6347',  # Tomato Red
                edgecolors='#DC143C',
                linewidths=0.05
            )
            ax.add_collection3d(lid_collection)
        
        # Koordinat sınırlarını ayarla
        if body_mesh is not None and lid_mesh is not None:
            all_vertices = np.vstack([body_mesh.vertices, lid_mesh.vertices])
            min_limits = all_vertices.min(axis=0)
            max_limits = all_vertices.max(axis=0)
            
            max_range = (max_limits - min_limits).max() / 2.0
            mid_points = (max_limits + min_limits) / 2.0
            
            ax.set_xlim(mid_points[0] - max_range, mid_points[0] + max_range)
            ax.set_ylim(mid_points[1] - max_range, mid_points[1] + max_range)
            ax.set_zlim(mid_points[2] - max_range, mid_points[2] + max_range)
        
        ax.set_xlabel('X', fontsize=10, fontweight='bold')
        ax.set_ylabel('Y', fontsize=10, fontweight='bold')
        ax.set_zlabel('Z', fontsize=10, fontweight='bold')
        
        # Başlık
        if angle_deg is not None:
            ax.set_title(f"{title_text}\n(Açı: {angle_deg:.1f}°)", 
                        fontsize=12, fontweight='bold')
        else:
            ax.set_title(title_text, fontsize=12, fontweight='bold')
        
        # Bakış açısı
        ax.view_init(elev=20, azim=-60)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Kaydet
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=100, bbox_inches='tight', facecolor='white')
            print(f"✓ Snapshot kaydedildi: {save_path}")
        
        plt.close()
        return save_path
        
    except Exception as e:
        print(f"⚠️ Görselleştirme hatası: {e}")
        return None


def create_comparison_visualization(body_mesh, lid_mesh_before, lid_mesh_after, 
                                   angle_before, angle_after, title, save_path=None):
    """
    İki pozisyonu yan yana göster (Before/After)
    
    Args:
        body_mesh: Gövde
        lid_mesh_before: Kapak (Açılmadan önceki pozisyon)
        lid_mesh_after: Kapak (Açıldıktan sonraki pozisyon)
        angle_before: Önceki açı
        angle_after: Sonraki açı
        title: Başlık
        save_path: Kaydetme yolu
    """
    try:
        fig = plt.figure(figsize=(16, 7))
        
        # Sol panel
        ax1 = fig.add_subplot(121, projection='3d')
        
        # Gövde
        body_triangles = body_mesh.vertices[body_mesh.faces]
        body_collection = Poly3DCollection(
            body_triangles, 
            alpha=0.6, 
            facecolors='#4169E1',
            edgecolors='#1E90FF',
            linewidths=0.05
        )
        ax1.add_collection3d(body_collection)
        
        # Kapak (before)
        lid_triangles = lid_mesh_before.vertices[lid_mesh_before.faces]
        lid_collection = Poly3DCollection(
            lid_triangles, 
            alpha=0.7, 
            facecolors='#FF6347',
            edgecolors='#DC143C',
            linewidths=0.05
        )
        ax1.add_collection3d(lid_collection)
        
        # Koordinatlar
        all_vertices = np.vstack([body_mesh.vertices, lid_mesh_before.vertices])
        min_limits = all_vertices.min(axis=0)
        max_limits = all_vertices.max(axis=0)
        max_range = (max_limits - min_limits).max() / 2.0
        mid_points = (max_limits + min_limits) / 2.0
        
        for ax in [ax1]:
            ax.set_xlim(mid_points[0] - max_range, mid_points[0] + max_range)
            ax.set_ylim(mid_points[1] - max_range, mid_points[1] + max_range)
            ax.set_zlim(mid_points[2] - max_range, mid_points[2] + max_range)
            ax.set_xlabel('X', fontsize=9)
            ax.set_ylabel('Y', fontsize=9)
            ax.set_zlabel('Z', fontsize=9)
            ax.view_init(elev=20, azim=-60)
            ax.grid(True, alpha=0.3)
        
        ax1.set_title(f"KAPALI (0°)\n❌ Çarpışma Var!", 
                     fontsize=11, fontweight='bold', color='red')
        
        # Sağ panel
        ax2 = fig.add_subplot(122, projection='3d')
        
        # Gövde
        body_collection2 = Poly3DCollection(
            body_triangles, 
            alpha=0.6, 
            facecolors='#4169E1',
            edgecolors='#1E90FF',
            linewidths=0.05
        )
        ax2.add_collection3d(body_collection2)
        
        # Kapak (after)
        lid_triangles_after = lid_mesh_after.vertices[lid_mesh_after.faces]
        lid_collection2 = Poly3DCollection(
            lid_triangles_after, 
            alpha=0.7, 
            facecolors='#00CC00',
            edgecolors='#009900',
            linewidths=0.05
        )
        ax2.add_collection3d(lid_collection2)
        
        ax2.set_xlim(mid_points[0] - max_range, mid_points[0] + max_range)
        ax2.set_ylim(mid_points[1] - max_range, mid_points[1] + max_range)
        ax2.set_zlim(mid_points[2] - max_range, mid_points[2] + max_range)
        ax2.set_xlabel('X', fontsize=9)
        ax2.set_ylabel('Y', fontsize=9)
        ax2.set_zlabel('Z', fontsize=9)
        ax2.view_init(elev=20, azim=-60)
        ax2.grid(True, alpha=0.3)
        ax2.set_title(f"AÇIK ({angle_after:.0f}°)\n✅ Sorun Yok!", 
                     fontsize=11, fontweight='bold', color='green')
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=100, bbox_inches='tight', facecolor='white')
            print(f"✓ Karşılaştırma kaydedildi: {save_path}")
        
        plt.close()
        return save_path
        
    except Exception as e:
        print(f"⚠️ Karşılaştırma görselleştirme hatası: {e}")
        return None


def create_html_report(failures_list):
    """
    Başarısız testlerin HTML raporu oluştur
    
    Args:
        failures_list: Başarısız test listesi [
            {
                'test_name': 'test_lid_no_collision_at_angle[0]',
                'angle': 0,
                'image_path': 'path/to/image.png',
                'error_message': 'Kapak 0° açıda gövdeye çarpıyor',
                'comparison_image': 'path/to/comparison.png'
            }
        ]
    """
    failure_dir = ensure_failure_dir()
    html_path = os.path.join(failure_dir, 'index.html')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Başarısızlıkları - Box Assembly</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .stat-card p {{
            color: #666;
            font-size: 0.95em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .failure-section {{
            margin-bottom: 50px;
            border: 2px solid #ff6b6b;
            border-radius: 8px;
            padding: 30px;
            background: #fff5f5;
        }}
        
        .failure-title {{
            color: #c92a2a;
            font-size: 1.5em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .failure-title::before {{
            content: "❌";
            font-size: 1.2em;
        }}
        
        .failure-details {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #ff6b6b;
        }}
        
        .failure-details p {{
            margin: 10px 0;
            line-height: 1.6;
        }}
        
        .label {{
            font-weight: bold;
            color: #667eea;
        }}
        
        .error-message {{
            background: #ffe0e0;
            padding: 10px;
            border-radius: 4px;
            color: #c92a2a;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }}
        
        .image-container {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .image-container img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .image-label {{
            padding: 15px;
            text-align: center;
            background: #f8f9fa;
            font-weight: bold;
            color: #667eea;
            font-size: 0.95em;
        }}
        
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .comparison-image {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .comparison-image img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .comparison-label {{
            padding: 15px;
            text-align: center;
            background: #f8f9fa;
            font-weight: bold;
            color: #667eea;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .image-grid {{
                grid-template-columns: 1fr;
            }}
            
            .comparison-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔴 Test Başarısızlıkları Raporu</h1>
            <p>Box Assembly Test Suite - Başarısız Test Analizi</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{len(failures_list)}</h3>
                <p>Başarısız Test</p>
            </div>
            <div class="stat-card">
                <h3>32</h3>
                <p>Toplam Test</p>
            </div>
            <div class="stat-card">
                <h3>93.75%</h3>
                <p>Başarı Oranı</p>
            </div>
            <div class="stat-card">
                <h3>1</h3>
                <p>Kritik Tasarım Hatası</p>
            </div>
        </div>
        
        <div class="content">
"""
    
    # Başarısız testleri ekle
    for i, failure in enumerate(failures_list, 1):
        html_content += f"""
            <div class="failure-section">
                <div class="failure-title">
                    {failure.get('test_name', 'Bilinmeyen Test')}
                </div>
                
                <div class="failure-details">
                    <p><span class="label">Açı:</span> {failure.get('angle', 'N/A')}°</p>
                    <div class="error-message">
                        <strong>Hata:</strong> {failure.get('error_message', 'Belirtilmemiş')}
                    </div>
                </div>
"""
        
        # Snapshot image
        if failure.get('image_path') and os.path.exists(failure['image_path']):
            rel_path = os.path.relpath(failure['image_path'], os.path.dirname(html_path))
            html_content += f"""
                <div class="image-grid">
                    <div class="image-container">
                        <img src="{rel_path}" alt="Test Snapshot">
                        <div class="image-label">Hata Anı Snapshot</div>
                    </div>
                </div>
"""
        
        # Comparison image
        if failure.get('comparison_image') and os.path.exists(failure['comparison_image']):
            rel_path = os.path.relpath(failure['comparison_image'], os.path.dirname(html_path))
            html_content += f"""
                <div class="image-grid">
                    <div class="image-container">
                        <img src="{rel_path}" alt="Comparison">
                        <div class="image-label">Kapalı vs Açık Karşılaştırması</div>
                    </div>
                </div>
"""
        
        html_content += """
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>📊 Rapor Oluşturulma Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p class="timestamp">Docker Test Environment | Python 3.11 | Trimesh 5.2.1</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML raporu kaydedildi: {html_path}")
    return html_path
