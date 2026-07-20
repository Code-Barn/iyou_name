// Build script for iyou_chart_kernel
// Sets required environment variables and linker flags for ImageMagick

fn main() {
    // Set environment variables for ImageMagick - required for magick_rust build
    println!("cargo:rustc-env=MAGICKCORE_HDRI_ENABLE=1");
    println!("cargo:rustc-env=MAGICKCORE_QUANTUM_DEPTH=16");

    // For macOS Clang compatibility
    println!("cargo:rustc-env=__ALLOW_UNNAMED_STRUCTURES=1");

    // Set linker flags for Unix systems
    #[cfg(unix)]
    {
        println!("cargo:rustc-link-lib=dylib=MagickWand-7.Q16HDRI");
        println!("cargo:rustc-link-lib=dylib=MagickCore-7.Q16HDRI");
    }

    // Rerun if any source files change
    println!("cargo:rerun-if-changed=src/");
    println!("cargo:rerun-if-changed=build.rs");
}
