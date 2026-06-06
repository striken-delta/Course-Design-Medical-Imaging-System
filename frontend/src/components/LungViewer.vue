<template>
  <div class="lung-viewer">
    <div ref="containerRef" class="viewer-container"></div>
    <div class="controls">
      <el-button size="small" @click="resetView">重置视角</el-button>
      <el-tag v-if="selectedMarker" type="warning" size="small" class="marker-info">
        切片 {{ selectedMarker.slice_id }} | 置信度 {{ (selectedMarker.confidence * 100).toFixed(1) }}%
      </el-tag>
    </div>
    <el-dialog
      v-model="dialogVisible"
      title="标记点详情"
      width="400px"
    >
      <template v-if="selectedMarker">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="标记ID">{{ selectedMarker.id }}</el-descriptions-item>
          <el-descriptions-item label="关联切片">{{ selectedMarker.slice_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="X 坐标">{{ selectedMarker.x.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="Y 坐标">{{ selectedMarker.y.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="Z 坐标">{{ selectedMarker.z.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="置信度">{{ (selectedMarker.confidence * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedMarker.label" label="预测标签">
            <el-tag :type="selectedMarker.label === 'nodule' ? 'danger' : 'success'" size="small">
              {{ selectedMarker.label === 'nodule' ? '疑似结节' : '未发现结节' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import type { Lung3DMarker } from '@/types'

const props = defineProps<{
  markers?: Lung3DMarker[]
  patientMode?: boolean
}>()

const containerRef = ref<HTMLElement>()
const dialogVisible = ref(false)
const selectedMarker = ref<Lung3DMarker | null>(null)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let markerObjects: THREE.Mesh[] = []
let animationId: number

function initScene() {
  if (!containerRef.value) return

  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight || 500

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x1a1a2e)

  // Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(3, 2, 5)

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  containerRef.value.appendChild(renderer.domElement)

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 2
  controls.maxDistance = 10

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 10, 7)
  scene.add(directionalLight)

  // Placeholder lung shape (ellipsoid)
  const geometry = new THREE.SphereGeometry(1.2, 64, 48)
  geometry.scale(1, 1.3, 0.8)
  const material = new THREE.MeshPhongMaterial({
    color: 0xff9999,
    specular: 0x333333,
    shininess: 30,
    transparent: true,
    opacity: 0.5,
    wireframe: false
  })
  const lung = new THREE.Mesh(geometry, material)
  scene.add(lung)

  // Left lung
  const leftGeom = new THREE.SphereGeometry(0.9, 48, 36)
  leftGeom.scale(1, 1.3, 0.7)
  const leftLung = new THREE.Mesh(leftGeom, material.clone())
  leftLung.position.set(-1.0, 0, 0)
  scene.add(leftLung)

  // Right lung
  const rightGeom = new THREE.SphereGeometry(0.95, 48, 36)
  rightGeom.scale(1, 1.3, 0.7)
  const rightLung = new THREE.Mesh(rightGeom, material.clone())
  rightLung.position.set(1.0, 0, 0)
  scene.add(rightLung)

  // Grid
  const gridHelper = new THREE.GridHelper(6, 20, 0x444466, 0x222244)
  gridHelper.position.y = -2
  scene.add(gridHelper)

  // Axes
  const axesHelper = new THREE.AxesHelper(2)
  scene.add(axesHelper)

  // Render markers
  renderMarkers()

  // Raycaster for click detection
  const raycaster = new THREE.Raycaster()
  const mouse = new THREE.Vector2()

  renderer.domElement.addEventListener('click', (event: MouseEvent) => {
    const rect = renderer.domElement.getBoundingClientRect()
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(markerObjects)
    if (intersects.length > 0) {
      const obj = intersects[0].object
      const markerData = obj.userData.marker as Lung3DMarker
      if (markerData) {
        selectedMarker.value = markerData
        dialogVisible.value = true
      }
    }
  })

  // Animation
  function animate() {
    animationId = requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()
}

function renderMarkers() {
  // Remove old markers
  markerObjects.forEach(m => scene.remove(m))
  markerObjects = []

  if (!props.markers || props.markers.length === 0) return

  const markerGeom = new THREE.SphereGeometry(0.08, 16, 16)
  const noduleMat = new THREE.MeshStandardMaterial({ color: 0xff4444, emissive: 0xff2222, emissiveIntensity: 0.5 })
  const nonNoduleMat = new THREE.MeshStandardMaterial({ color: 0x4444ff, emissive: 0x2222ff, emissiveIntensity: 0.5 })

  props.markers.forEach(marker => {
    const mat = marker.label === 'nodule' ? noduleMat : nonNoduleMat
    const mesh = new THREE.Mesh(markerGeom, mat)
    mesh.position.set(marker.x, marker.y, marker.z)
    mesh.userData = { marker }
    mesh.scale.setScalar(0.5 + marker.confidence * 1.5)
    scene.add(mesh)
    markerObjects.push(mesh)
  })
}

function resetView() {
  camera.position.set(3, 2, 5)
  controls.target.set(0, 0, 0)
  controls.update()
}

function handleResize() {
  if (!containerRef.value || !renderer) return
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight || 500
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

watch(() => props.markers, () => {
  if (scene) {
    renderMarkers()
  }
}, { deep: true })

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (renderer) {
    renderer.dispose()
  }
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.lung-viewer {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e6e6e6;
  background: #1a1a2e;
}
.viewer-container {
  width: 100%;
  min-height: 500px;
  cursor: grab;
}
.viewer-container:active {
  cursor: grabbing;
}
.controls {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.marker-info {
  background: rgba(0, 0, 0, 0.6) !important;
  color: #fff !important;
  border: none !important;
}
</style>
