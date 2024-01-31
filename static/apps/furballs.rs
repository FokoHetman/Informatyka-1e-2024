use std::{
  env,
  fs,
  io::{Read, Write},
  path::Path,
  io,
  io::prelude::*,
  io::BufReader,
  fs::File,
  convert::TryInto,
  path::PathBuf,
  collections::VecDeque,
};


fn main() -> std::io::Result<()> {
  let args: Vec<String> = env::args().collect();                                                              // env vars


  let path = Path::new(&args[2]);

  /*if !anpath.is_dir() {                                                                                      // make sure directory's correct
    println!("Given argument [ {} ] is not a directory!", args[3]);
    return Ok(());
  }*/


  let mut ball = Furball {mode: "n".to_string(), logging: "d".to_string(), encoding: "h".to_string()};   // create a simple encoder/decoder

  let modes: Vec<String> = ["r".to_string(), "e".to_string()].to_vec();
  let logs: Vec<String> = ["w".to_string(), "d".to_string(), "a".to_string()].to_vec();
  let codex: Vec<String> = ["f".to_string(), "h".to_string()].to_vec();

  for i in args[1].chars() {                                                                           // parse args
    if modes.contains(&i.to_string()) {
      ball.mode = i.to_string();
    }
    else if logs.contains(&i.to_string()) {
      ball.logging = i.to_string();
    }
    else if codex.contains(&i.to_string()) {
      ball.encoding = i.to_string();
    }

  }


  if ball.mode=="n".to_string() {
    println!("Didn't specify mode!");
    return Ok(());
  }
  else if ball.mode=="r".to_string() {

    let mut furball = fs::File::create(format!("{}", args[3]))?;
    furball.write_all(b"");

    if ball.logging=="d".to_string() || ball.logging=="a".to_string() {
      println!("Scanning directory...");
    }
      //read_dir(&path, &args[3], &mut ball); // read the directory
    let mut rev_dirs = list_dir(PathBuf::from(path))?;
       //let mut dirs: Vec<&Path> = [].to_vec();
    let mut dirs = VecDeque::new();
    for i in &rev_dirs {
      dirs.push_front(i);
    }
    if ball.logging=="d".to_string() || ball.logging=="a".to_string() {
      println!("Found directories:\n{:#?}", dirs);
    }

    for i in dirs {
      ball.encode(i, &args[3]);
    }
    // furball.write_all(b"fokinit ")?;
    println!("Finished encoding all found directories.");
    Ok(())

  }
  else if ball.mode=="e".to_string() {

    ball.decode(&path);  
    Ok(())
  } else {
    println!("Mode pick returned an error");
    Ok(())
  }
}


fn list_dir(dir: PathBuf) -> io::Result<Vec<PathBuf>> {

  let mut dirs: Vec<PathBuf> = [].to_vec();
  if dir.is_dir() {
    for obj in fs::read_dir(dir.clone())? {
      let mut path = obj?.path();
      if path.is_dir() {
        dirs.append(&mut list_dir(path.clone())?);
      } else {
        dirs.push(path.clone());
      }
    }
  }
  dirs.push(dir.clone());
  return Ok(dirs)
}


fn read_dir(dir: &Path, furball: &str, mut ball: &mut Furball) -> io::Result<()> {
  if dir.is_dir() {
    for obj in fs::read_dir(dir)? {
      let path = obj?.path();
      if path.is_dir() {
        read_dir(&path, furball.clone(), ball);
        ball.encode(&path, furball);

      } else {
        let file = fs::File::open(path.clone())?;
        let mut ctn = String::new();
        let mut buffer = BufReader::new(file);
        buffer.read_to_string(&mut ctn)?;
        println!("Contents of file {:#?}: {}", &path, ctn);
        ball.encode(&path, furball);

      }
    }
  } else {
    let file = fs::File::open(dir.clone())?;
    let mut ctn = String::new();
    let mut buffer = BufReader::new(file);
    buffer.read_to_string(&mut ctn)?;
    println!("Contents of file {:#?}: {}", &dir, ctn);
    ball.encode(&dir, furball);
  println!("Finished...");
  }
  Ok(())
}


struct Furball {
  mode: String,
  logging: String,
  encoding: String,
}


trait FurballTrait {
  fn encode(&mut self, path: &Path, furball: &str) -> io::Result<()>;
  fn decode(&mut self, path: &Path) -> io::Result<()>;
}

impl FurballTrait for Furball {
  fn encode(&mut self, path: &Path, furball: &str) -> io::Result<()> {
    if self.logging=="d".to_string() || self.logging=="a".to_string() {
      println!("Encoding {:#?}...", path);
    }
    let mut curr = fs::File::open(furball.to_string())?;
    let mut all = String::new();
    curr.read_to_string(&mut all);

    let mut newfile = fs::File::open(path)?;

    let isdir = path.is_dir();
    let mut new = String::new();
    if !isdir {
      newfile.read_to_string(&mut new);
    }
    let mut nall = String::new();
    if self.encoding=="h".to_string() {
      if isdir {
        
        nall = format!("{}\n[FURDIR-HEADER] Zfur-location=``{:#?}``[/FURDIR-HEADER]", all, &path);

      } else {
        nall = format!("{}\n[FURFILE-HEADER] Zfur-location=``{:#?}``;{};Zfur_data{}{}[/FURFILE-HEADER]", all, &path, "FUR-BONE", "eq", new);
      }

    }
    fs::write(furball.to_string(), nall);

    if self.logging=="d".to_string() || self.logging=="a".to_string() {
      println!("Finished encoding.");
    }

    Ok(())
  }


  fn decode(&mut self, path: &Path) -> io::Result<()> {


    let mut file = fs::File::open(path)?;
    let mut content = String::new();

    file.read_to_string(&mut content);

    let mut buffer:String = String::new();
    for i in content.chars() {
      buffer = buffer + &i.to_string();


      if buffer.contains("[FURDIR-HEADER]") && buffer.contains("[/FURDIR-HEADER]") {

        if self.encoding=="h".to_string() {
          let mut fork = buffer.replace("[FURDIR-HEADER]","")
              .replace("[/FURDIR-HEADER]","");

          let locs: Vec<&str> = fork.split("fur-location=").collect::<Vec<&str>>();

          let loc: &str = &locs[1].replace("``\"", "").replace("\"``","");

          if self.logging=="d".to_string() || self.logging=="a".to_string() {
            println!("Creating a directory: {}", loc);
          }
          fs::create_dir(loc);
        }

        buffer = "".to_string();
      }


      if buffer.contains("[FURFILE-HEADER]") && buffer.contains("[/FURFILE-HEADER]") {
        let mut fork= buffer.replace("[FURFILE-HEADER]","")
            .replace("[/FURFILE-HEADER]","");

        let locs: Vec<&str> = fork.split(&format!(";{};", "FUR-BONE")).collect::<Vec<&str>>();


        let loc: &str = &locs[0].split("fur-location=").collect::<Vec<&str>>()[1].replace("\"``", "").replace("``\"", "");

        let src: &str = &locs[1].split("dataeq").collect::<Vec<&str>>()[1];

        println!("{}", loc);
        let mut nwrite = fs::File::create(loc)?;

        nwrite.write_all(src.as_bytes());
        if self.logging=="d".to_string() || self.logging=="a".to_string() {
          println!("Creating a file: {}", loc);
        }
        buffer = "".to_string();
      }
    }
    Ok(())
  }
}
